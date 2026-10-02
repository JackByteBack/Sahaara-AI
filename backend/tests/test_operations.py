"""Tests for the added operations surface (see README "What was built" additions):

· Case export (CSV/JSON, audited, sanitized — no transcript)
· Queue filters (language / safety / assigned / min_priority)
· Case assignment workflow (supervisor assigns, operator self-assign only)
· Follow-up reminders (due date, completion) + derived notification feed
· Profile settings (display name, language, password change)
· Regression: flag decisions & follow-up edits must PERSIST (JSON change tracking)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from main import app
from app.database import SessionLocal, init_db
from app.seed import seed


@pytest.fixture(scope="module")
def client():
    init_db()
    db = SessionLocal()
    seed(db)
    db.close()
    with TestClient(app) as c:
        yield c


def _login(client, username, password):
    res = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture(scope="module")
def supervisor(client):
    return _login(client, "supervisor", "super123")


@pytest.fixture(scope="module")
def operator(client):
    return _login(client, "operator", "operator123")


@pytest.fixture(scope="module")
def case_id(client, operator):
    res = client.post("/api/v1/cases/start",
                      json={"initial_language": "hi", "mode": "text", "consent": True},
                      headers=operator)
    assert res.status_code == 200
    return res.json()["id"]


# ── Export ────────────────────────────────────────────────────────────
def test_export_csv_is_sanitized_and_audited(client, supervisor, case_id):
    res = client.get("/api/v1/cases/export", params={"format": "csv"}, headers=supervisor)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment" in res.headers["content-disposition"]
    body = res.text
    assert "case_number,status" in body.splitlines()[0]
    # transcript never leaves via export (data minimization)
    assert "transcript" not in body.splitlines()[0]

    audit = client.get("/api/v1/audit", headers=supervisor).json()["entries"]
    assert any(e["action"] == "exported" for e in audit)


def test_export_json(client, supervisor):
    res = client.get("/api/v1/cases/export", params={"format": "json"}, headers=supervisor)
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == len(data["cases"])
    assert "transcript" not in data["cases"][0]


# ── Queue filters ─────────────────────────────────────────────────────
def test_filters_language_and_safety(client, supervisor):
    res = client.get("/api/v1/cases", params={"safety": "true"}, headers=supervisor)
    assert res.status_code == 200
    assert all(c["safety_override"] for c in res.json()["cases"])

    res = client.get("/api/v1/cases", params={"assigned": "mine"}, headers=supervisor)
    me = client.get("/api/v1/auth/me", headers=supervisor).json()["id"]
    assert all(c["assigned_to"] == me for c in res.json()["cases"])


# ── Assignment workflow ───────────────────────────────────────────────
def test_assignment_roundtrip_and_persistence(client, supervisor, operator, case_id):
    me = client.get("/api/v1/auth/me", headers=supervisor).json()["id"]

    res = client.patch(f"/api/v1/cases/{case_id}", json={"assigned_to": me}, headers=supervisor)
    assert res.status_code == 200
    assert res.json()["assigned_to"] == me
    assert res.json()["assigned_to_username"] == "supervisor"

    # persists on refetch (JSON/scalar change tracking)
    fresh = client.get(f"/api/v1/cases/{case_id}", headers=supervisor).json()
    assert fresh["assigned_to"] == me

    # operator cannot assign to someone else
    res = client.patch(f"/api/v1/cases/{case_id}",
                       json={"assigned_to": "someone-else"}, headers=operator)
    assert res.status_code in (400, 403)  # 403 for role, 400 for unknown user

    # clear
    res = client.patch(f"/api/v1/cases/{case_id}", json={"assigned_to": ""}, headers=supervisor)
    assert res.json()["assigned_to"] is None


# ── Flag decision regression (JSON in-place mutation bug) ─────────────
def test_flag_decision_persists(client, operator, supervisor, case_id):
    client.post(f"/api/v1/cases/{case_id}/segments",
                json={"text": "I want to die, I cannot take this anymore.", "speaker": "caller"},
                headers=operator)
    fresh = client.get(f"/api/v1/cases/{case_id}", headers=operator).json()
    assert fresh["ai_flags"], "expected AI flags after distress transcript"
    flag_id = fresh["ai_flags"][0]["id"]

    res = client.post(f"/api/v1/cases/{case_id}/flags/{flag_id}/decision",
                      json={"decision": "confirm", "notes": "verified"}, headers=supervisor)
    assert res.status_code == 200

    after = client.get(f"/api/v1/cases/{case_id}", headers=operator).json()
    flag = next(f for f in after["ai_flags"] if f["id"] == flag_id)
    assert flag["human_decision"] == "confirm"
    assert flag["status"] == "confirmed"


# ── Follow-ups + reminders ────────────────────────────────────────────
def test_followup_due_completion_and_feed(client, supervisor, case_id):
    res = client.post(f"/api/v1/cases/{case_id}/followups",
                      json={"stage": "followup", "note": "call back tomorrow", "due_at": "2020-01-01"},
                      headers=supervisor)
    assert res.status_code == 200
    fid = res.json()["followup"]["id"]
    assert res.json()["followup"]["completed"] is False

    # overdue follow-up shows up in the notification feed
    feed = client.get("/api/v1/notifications", headers=supervisor).json()
    assert any(n["id"] == f"followup-{case_id}-{fid}" for n in feed["notifications"])

    # completing it persists and removes it from the feed
    res = client.patch(f"/api/v1/cases/{case_id}/followups/{fid}",
                       json={"completed": True, "outcome": "reached"}, headers=supervisor)
    assert res.status_code == 200 and res.json()["followup"]["completed"] is True

    fresh = client.get(f"/api/v1/cases/{case_id}", headers=supervisor).json()
    entry = next(f for f in fresh["followups"] if f["id"] == fid)
    assert entry["completed"] is True and entry["completed_by"] == "supervisor"

    feed = client.get("/api/v1/notifications", headers=supervisor).json()
    assert not any(n["id"] == f"followup-{case_id}-{fid}" for n in feed["notifications"])


def test_notifications_feed_shape(client, supervisor):
    res = client.get("/api/v1/notifications", headers=supervisor)
    assert res.status_code == 200
    data = res.json()
    assert "notifications" in data and "counts" in data
    # safety-override items sort first
    if data["notifications"]:
        assert data["notifications"][0]["severity"] == "critical"


# ── Profile settings ──────────────────────────────────────────────────
def test_profile_update_and_password_change(client, supervisor):
    res = client.patch("/api/v1/auth/me", json={"display_name": "Test Supervisor"},
                       headers=supervisor)
    assert res.status_code == 200 and res.json()["display_name"] == "Test Supervisor"

    # wrong current password rejected
    res = client.patch("/api/v1/auth/me",
                       json={"current_password": "nope", "new_password": "newpass123"},
                       headers=supervisor)
    assert res.status_code == 400

    # weak new password rejected
    res = client.patch("/api/v1/auth/me",
                       json={"current_password": "super123", "new_password": "short"},
                       headers=supervisor)
    assert res.status_code == 400

    # no-op rejected
    assert client.patch("/api/v1/auth/me", json={}, headers=supervisor).status_code == 400

    # profile changes are audited
    audit = client.get("/api/v1/audit", headers=supervisor).json()["entries"]
    assert any(e["action"] == "settings" for e in audit)


# ── Root endpoint (no more {"detail":"Not Found"} at /) ───────────────
def test_root_index(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Sahaara AI" and data["health"] == "/health"
    assert "demo_logins" in data

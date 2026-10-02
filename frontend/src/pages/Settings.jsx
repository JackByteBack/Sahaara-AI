import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, getToken, getUser, setSession } from "../api/client";
import { ROLE_LABELS } from "../api/roles";
import { useSeo } from "../lib/seo";
import { Toasts, useToasts } from "../components/ui";

export default function Settings() {
  useSeo({
    title: "Settings — Sahaara AI",
    description: "Profile, language, password and system settings for the Sahaara console.",
    path: "/settings",
  });

  const user = getUser();
  const { toasts, push, dismiss } = useToasts();
  const [profile, setProfile] = useState({
    display_name: user?.display_name || "",
    language: user?.language || "en",
  });
  const [pw, setPw] = useState({ current_password: "", new_password: "", confirm: "" });
  const [health, setHealth] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api("/health").then(setHealth).catch(() => setHealth({ status: "unreachable" }));
  }, []);

  const saveProfile = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const updated = await api("/api/v1/auth/me", { method: "PATCH", body: profile });
      setSession(getToken(), { ...user, ...updated });
      push("Profile updated (recorded in the audit trail).");
    } catch (err) {
      push(err.message, "danger");
    } finally {
      setBusy(false);
    }
  };

  const savePassword = async (e) => {
    e.preventDefault();
    if (pw.new_password !== pw.confirm) {
      push("New passwords do not match.", "danger");
      return;
    }
    setBusy(true);
    try {
      await api("/api/v1/auth/me", {
        method: "PATCH",
        body: { current_password: pw.current_password, new_password: pw.new_password },
      });
      setPw({ current_password: "", new_password: "", confirm: "" });
      push("Password changed (recorded in the audit trail).");
    } catch (err) {
      push(err.message, "danger");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page page-narrow">
      <Toasts toasts={toasts} dismiss={dismiss} />
      <h2>Settings.</h2>
      <p className="body-lg muted" style={{ marginTop: 8 }}>
        Profile, security and system status. Every change here is audited.
      </p>

      {/* Profile */}
      <form className="card" style={{ marginTop: 28 }} onSubmit={saveProfile}>
        <h4 style={{ marginBottom: 14 }}>Profile</h4>
        <div className="grid-2" style={{ gap: 14 }}>
          <label className="field">
            <span>Username</span>
            <input className="input" value={user?.username || ""} disabled />
          </label>
          <label className="field">
            <span>Role</span>
            <input className="input" value={ROLE_LABELS[user?.role] || user?.role || ""} disabled />
          </label>
          <label className="field">
            <span>Display name</span>
            <input className="input" value={profile.display_name} maxLength={100}
                   onChange={(e) => setProfile({ ...profile, display_name: e.target.value })} />
          </label>
          <label className="field">
            <span>Interface language</span>
            <select className="input" value={profile.language}
                    onChange={(e) => setProfile({ ...profile, language: e.target.value })}>
              <option value="en">English (en)</option>
              <option value="hi">हिन्दी (hi)</option>
              <option value="mr">मराठी (mr)</option>
            </select>
          </label>
        </div>
        <button className="btn btn-primary" style={{ marginTop: 16 }} disabled={busy}>Save profile</button>
      </form>

      {/* Password */}
      <form className="card" style={{ marginTop: 16 }} onSubmit={savePassword}>
        <h4 style={{ marginBottom: 14 }}>Change password</h4>
        <div className="grid-2" style={{ gap: 14 }}>
          <label className="field">
            <span>Current password</span>
            <input className="input" type="password" autoComplete="current-password"
                   value={pw.current_password}
                   onChange={(e) => setPw({ ...pw, current_password: e.target.value })} />
          </label>
          <span />
          <label className="field">
            <span>New password (min 8 characters)</span>
            <input className="input" type="password" autoComplete="new-password"
                   value={pw.new_password}
                   onChange={(e) => setPw({ ...pw, new_password: e.target.value })} />
          </label>
          <label className="field">
            <span>Confirm new password</span>
            <input className="input" type="password" autoComplete="new-password"
                   value={pw.confirm}
                   onChange={(e) => setPw({ ...pw, confirm: e.target.value })} />
          </label>
        </div>
        <button className="btn btn-outline" style={{ marginTop: 16 }}
                disabled={busy || !pw.current_password || !pw.new_password || !pw.confirm}>
          Change password
        </button>
      </form>

      {/* Session & safety */}
      <div className="card" style={{ marginTop: 16 }}>
        <h4 style={{ marginBottom: 10 }}>Session &amp; safety</h4>
        <ul className="list-reset col body-sm" style={{ gap: 8 }}>
          <li><strong>Safe Exit:</strong> press <kbd>Esc</kbd> twice (or the ✕ button) to wipe local storage, clipboard and cached data and leave to a neutral page.</li>
          <li><strong>Data minimization:</strong> this console keeps your session in sessionStorage only — closing the tab ends it.</li>
          <li><strong>Audit:</strong> profile and password changes, logins and case access are all recorded.</li>
          <li><strong>Log out</strong> from the nav pill when you finish your shift.</li>
        </ul>
      </div>

      {/* System status */}
      <div className="card" style={{ marginTop: 16 }}>
        <div className="row-between" style={{ marginBottom: 10 }}>
          <h4>System status</h4>
          {health && (
            <span className={`pill ${health.status === "ok" ? "pill-ok" : health.status === "unreachable" ? "pill-danger" : "pill-warn"}`}>
              {health.status || "…"}
            </span>
          )}
        </div>
        {!health ? (
          <p className="body-sm muted">Checking…</p>
        ) : health.status === "unreachable" ? (
          <p className="body-sm" style={{ color: "var(--danger)" }}>Backend unreachable — check the API server.</p>
        ) : (
          <ul className="list-reset col body-sm" style={{ gap: 6 }}>
            <li>Database: <strong>{health.database}</strong></li>
            <li>AI pipeline: <strong>{health.ai_pipeline}</strong>
              {health.ai_pipeline === "human_assessment" && " (Human Assessment Mode — rules engine active, graceful fallback Feature 1.14)"}
            </li>
            <li>API docs: <a href="/docs" target="_blank" rel="noreferrer">/docs</a> · Health: <code>/health</code></li>
          </ul>
        )}
        <p className="caption" style={{ marginTop: 10 }}>
          Question about your account? <Link to="/contact">Contact us</Link>.
        </p>
      </div>
    </div>
  );
}

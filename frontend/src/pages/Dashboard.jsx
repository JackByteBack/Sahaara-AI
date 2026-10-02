import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, getUser } from "../api/client";
import { can } from "../api/roles";
import { EmptyState, Loading, Modal, ScoreBar, Segmented, StatusPill, useToasts, Toasts } from "../components/ui";

export default function Dashboard() {
  const user = getUser();
  const navigate = useNavigate();
  const { toasts, push, dismiss } = useToasts();
  const [cases, setCases] = useState(null);
  const [stats, setStats] = useState(null);
  const [demos, setDemos] = useState([]);
  const [showNew, setShowNew] = useState(false);
  const [filter, setFilter] = useState("open");
  const [form, setForm] = useState({ initial_language: "en", mode: "text", trauma_mode: false, consent: true });

  const load = useCallback(async () => {
    try {
      const [c, s, d] = await Promise.all([
        api("/api/v1/cases"),
        api("/api/v1/analytics/overview").catch(() => null),
        api("/api/v1/demos").catch(() => ({ scenarios: [] })),
      ]);
      setCases(c.cases);
      setStats(s);
      setDemos(d.scenarios || []);
    } catch (err) {
      push(err.message, "danger");
      setCases([]);
    }
  }, [push]);

  useEffect(() => { load(); }, [load]);

  const startSession = async (body) => {
    try {
      const c = await api("/api/v1/cases/start", { method: "POST", body });
      push(`Session started — ${c.case_number}`);
      navigate(`/session/${c.id}`);
    } catch (err) {
      push(err.message, "danger");
    }
  };

  const startDemo = async (scenarioId) => {
    try {
      const res = await api(`/api/v1/demos/${scenarioId}/start`, { method: "POST" });
      push("Demo session ready — scripted lines will stream in.");
      navigate(`/session/${res.case.id}?demo=${scenarioId}`);
    } catch (err) {
      push(err.message, "danger");
    }
  };

  if (cases === null) return <div className="page"><Loading text="Loading queue" /></div>;

  const open = cases.filter((c) => c.status !== "closed");
  const overrideCount = open.filter((c) => c.safety_override).length;
  const visible = filter === "open" ? open : cases;

  return (
    <div className="page">
      <Toasts toasts={toasts} dismiss={dismiss} />

      <div className="row-between wrap" style={{ gap: 16 }}>
        <div>
          <h2>Review queue.</h2>
          <p className="body-lg muted" style={{ marginTop: 8 }}>
            Safety-first ordering. Every flag below is a suggestion awaiting your decision.
          </p>
        </div>
        {can(user.role, "case_create") && (
          <button className="btn btn-primary btn-lg" onClick={() => setShowNew(true)}>New session</button>
        )}
      </div>

      <div className="grid-4" style={{ marginTop: 40 }}>
        <div className="card">
          <p className="label muted">Open cases</p>
          <p className="dial-value" style={{ marginTop: 8 }}>{open.length}</p>
        </div>
        <div className="card" style={overrideCount ? { borderColor: "#fecdca", background: "var(--danger-soft)" } : undefined}>
          <p className="label muted">Safety overrides</p>
          <p className="dial-value" style={{ marginTop: 8, color: overrideCount ? "var(--danger)" : undefined }}>
            {overrideCount}
          </p>
        </div>
        <div className="card">
          <p className="label muted">AI pipeline</p>
          <p className="title" style={{ marginTop: 10 }}>
            {stats && stats.total_cases >= 0 ? "Human + AI assisted" : "Human + AI assisted"}
          </p>
          <p className="caption">Rules run even when generative AI is down.</p>
        </div>
        <div className="card">
          <p className="label muted">Total cases</p>
          <p className="dial-value" style={{ marginTop: 8 }}>{stats?.total_cases ?? "—"}</p>
        </div>
      </div>

      <div className="row-between wrap" style={{ marginTop: 48, marginBottom: 16 }}>
        <h4>Cases</h4>
        <Segmented
          value={filter}
          onChange={setFilter}
          options={[{ value: "open", label: "Open" }, { value: "all", label: "All" }]}
        />
      </div>

      {visible.length === 0 ? (
        <EmptyState
          title="No cases yet."
          subtitle="Start a live session or load a scripted demonstration scenario."
          action={can(user.role, "case_create") ? <button className="btn btn-primary" onClick={() => setShowNew(true)}>New session</button> : null}
        />
      ) : (
        <div className="col" style={{ gap: 12 }}>
          {visible.map((c) => (
            <Link key={c.id} to={`/cases/${c.id}`} style={{ textDecoration: "none" }}>
              <div className="card row-between wrap" style={{ gap: 16, ...(c.safety_override ? { borderColor: "#fecdca" } : {}) }}>
                <div className="col" style={{ gap: 6, minWidth: 240 }}>
                  <div className="row" style={{ gap: 8 }}>
                    <strong>{c.case_number}</strong>
                    <StatusPill status={c.status} />
                    {c.safety_override && <span className="pill pill-danger">Safety override</span>}
                    {c.is_demo && <span className="pill pill-outline">demo</span>}
                  </div>
                  <span className="caption">
                    {((c.language_info?.primary || {}).language || "en").toUpperCase()}
                    {" · "}flags {c.ai_flags?.length || 0}
                    {" · "}updated {c.updated_at ? new Date(c.updated_at).toLocaleString() : "—"}
                  </span>
                </div>
                <div style={{ minWidth: 220, flex: 1 }}>
                  <div className="row-between" style={{ marginBottom: 6 }}>
                    <span className="label muted">Review priority (operational)</span>
                    <span className="label mono">{Number(c.review_priority_score).toFixed(2)}</span>
                  </div>
                  <ScoreBar value={c.review_priority_score} danger={c.safety_override} />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      <div className="section">
        <h4>Demonstration scenarios</h4>
        <p className="muted body-sm" style={{ marginTop: 6 }}>
          Scripted multilingual conversations for training and evaluation (Feature 1.15).
        </p>
        <div className="grid-3" style={{ marginTop: 16 }}>
          {demos.map((d) => (
            <div key={d.id} className="card col" style={{ gap: 10 }}>
              <strong className="body-sm">{d.title}</strong>
              <span className="caption">{d.expected}</span>
              <div className="row-between">
                <span className="pill pill-outline">{d.language} · {d.line_count} lines</span>
                <button className="btn btn-soft btn-sm" disabled={!can(user.role, "case_create")}
                        onClick={() => startDemo(d.id)}>Run demo</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {showNew && (
        <Modal title="Start a session" onClose={() => setShowNew(false)}>
          <div className="col" style={{ gap: 16 }}>
            <label className="field">
              <span>Language</span>
              <select className="input" value={form.initial_language}
                      onChange={(e) => setForm({ ...form, initial_language: e.target.value })}>
                <option value="en">English</option>
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="mr">मराठी (Marathi)</option>
              </select>
            </label>
            <label className="field">
              <span>Session mode</span>
              <Segmented
                value={form.mode}
                onChange={(v) => setForm({ ...form, mode: v })}
                options={[
                  { value: "text", label: "Typed text" },
                  { value: "voice", label: "Voice (browser ASR)" },
                ]}
              />
            </label>
            <label className="field">
              <span>Trauma-informed mode (Feature 2.13)</span>
              <Segmented
                value={form.trauma_mode ? "on" : "off"}
                onChange={(v) => setForm({ ...form, trauma_mode: v === "on" })}
                options={[{ value: "off", label: "Off" }, { value: "on", label: "On" }]}
              />
            </label>
            <label className="row" style={{ gap: 10, cursor: "pointer" }}>
              <input type="checkbox" checked={form.consent}
                     onChange={(e) => setForm({ ...form, consent: e.target.checked })} />
              <span className="body-sm">Consent obtained from the caller for processing (Feature 1.10 — mandatory)</span>
            </label>
            <button className="btn btn-primary btn-lg" disabled={!form.consent}
                    onClick={() => startSession(form)}>
              Start session
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, download } from "../api/client";
import { EmptyState, Loading, ScoreBar, StatusPill, useToasts, Toasts } from "../components/ui";

const STATUSES = ["", "active", "reviewing", "referred", "closed"];
const LANGS = ["", "en", "hi", "mr"];

export default function Cases() {
  const [cases, setCases] = useState(null);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [language, setLanguage] = useState("");
  const [scope, setScope] = useState(""); // "" | safety | mine | unassigned
  const [exporting, setExporting] = useState(null);
  const { toasts, push, dismiss } = useToasts();

  useEffect(() => {
    const params = { q };
    if (status) params.status = status;
    if (language) params.language = language;
    if (scope === "safety") params.safety = "true";
    if (scope === "mine" || scope === "unassigned") params.assigned = scope;
    api("/api/v1/cases", { params })
      .then((d) => setCases(d.cases))
      .catch((err) => { push(err.message, "danger"); setCases([]); });
  }, [q, status, language, scope, push]);

  const doExport = async (format) => {
    setExporting(format);
    try {
      await download(`/api/v1/cases/export?format=${format}`, `sahaara-cases.${format}`);
      push(`Export downloaded — the export is recorded in the audit trail.`);
    } catch (err) {
      push(err.message, "danger");
    } finally {
      setExporting(null);
    }
  };

  if (!cases) return <div className="page"><Loading text="Loading cases" /></div>;

  return (
    <div className="page">
      <Toasts toasts={toasts} dismiss={dismiss} />
      <div className="row-between wrap" style={{ gap: 16 }}>
        <div>
          <h2>Cases.</h2>
          <p className="body-lg muted" style={{ marginTop: 8 }}>Full lifecycle: active → reviewing → referred → closed.</p>
        </div>
        <div className="row wrap" style={{ gap: 8 }}>
          <input className="input" style={{ maxWidth: 220 }} placeholder="Search case number…"
                 value={q} onChange={(e) => setQ(e.target.value)} />
          <button className="btn btn-outline btn-sm" disabled={!!exporting}
                  onClick={() => doExport("csv")}>
            {exporting === "csv" ? "…" : "Export CSV"}
          </button>
          <button className="btn btn-outline btn-sm" disabled={!!exporting}
                  onClick={() => doExport("json")}>
            {exporting === "json" ? "…" : "Export JSON"}
          </button>
        </div>
      </div>

      {/* Filters — queue triage at a glance */}
      <div className="row wrap card-soft" style={{ gap: 12, marginTop: 20, padding: 14 }}>
        <span className="label muted">Filters</span>
        <select className="input" style={{ maxWidth: 160 }} value={status}
                onChange={(e) => setStatus(e.target.value)} aria-label="Status">
          {STATUSES.map((s) => <option key={s} value={s}>{s || "Any status"}</option>)}
        </select>
        <select className="input" style={{ maxWidth: 160 }} value={language}
                onChange={(e) => setLanguage(e.target.value)} aria-label="Language">
          {LANGS.map((l) => <option key={l} value={l}>{l ? l.toUpperCase() : "Any language"}</option>)}
        </select>
        <select className="input" style={{ maxWidth: 190 }} value={scope}
                onChange={(e) => setScope(e.target.value)} aria-label="Scope">
          <option value="">Any assignment</option>
          <option value="safety">Safety override only</option>
          <option value="mine">Assigned to me</option>
          <option value="unassigned">Unassigned</option>
        </select>
        {(q || status || language || scope) && (
          <button className="btn btn-soft btn-sm"
                  onClick={() => { setQ(""); setStatus(""); setLanguage(""); setScope(""); }}>
            Clear
          </button>
        )}
        <span className="caption" style={{ marginLeft: "auto" }}>{cases.length} case{cases.length === 1 ? "" : "s"}</span>
      </div>

      <div style={{ marginTop: 24 }}>
        {cases.length === 0 ? (
          <EmptyState title="No cases match." subtitle="Adjust the filters or start a session from the queue page." />
        ) : (
          <div className="card card-flush table-scroll">
            <table className="data">
              <thead>
                <tr>
                  <th>Case</th><th>Status</th><th>Language</th><th>Flags</th>
                  <th style={{ width: 220 }}>Priority</th><th>Safety</th><th>Assigned</th><th></th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr key={c.id}>
                    <td>
                      <strong>{c.case_number}</strong>
                      {c.is_demo && <span className="pill pill-outline" style={{ marginLeft: 8 }}>demo</span>}
                    </td>
                    <td><StatusPill status={c.status} /></td>
                    <td>{((c.language_info?.primary || {}).language || "en").toUpperCase()}</td>
                    <td className="mono">{c.ai_flags?.length || 0}</td>
                    <td><ScoreBar value={c.review_priority_score} danger={c.safety_override} /></td>
                    <td>{c.safety_override ? <span className="pill pill-danger">override</span> : <span className="caption">—</span>}</td>
                    <td className="caption">{c.assigned_to_username || <span className="faint">unassigned</span>}</td>
                    <td><Link className="btn btn-soft btn-sm" to={`/cases/${c.id}`}>Open</Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

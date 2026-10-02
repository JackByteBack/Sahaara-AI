import { useEffect, useState } from "react";
import { api } from "../api/client";
import { Loading, useToasts, Toasts } from "../components/ui";

function Bar({ label, value, max, suffix }) {
  const pct = max ? Math.round((value / max) * 100) : 0;
  return (
    <div style={{ marginBottom: 10 }}>
      <div className="row-between body-sm">
        <span>{label}</span>
        <span className="mono muted">{value}{suffix || ""}</span>
      </div>
      <div className="score-track" style={{ marginTop: 4 }}>
        <div className="score-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function Analytics() {
  const [data, setData] = useState(null);
  const { toasts, push, dismiss } = useToasts();

  useEffect(() => {
    api("/api/v1/analytics/overview").then(setData).catch((err) => push(err.message, "danger"));
  }, [push]);

  if (!data) return <div className="page"><Loading text="Loading analytics" /></div>;

  const maxDay = Math.max(1, ...Object.values(data.cases_by_day));
  const maxLang = Math.max(1, ...Object.values(data.language_distribution));
  const maxPrio = Math.max(1, ...Object.values(data.priority_distribution));

  return (
    <div className="page">
      <Toasts toasts={toasts} dismiss={dismiss} />
      <h2>Analytics.</h2>
      <p className="body-lg muted" style={{ marginTop: 8 }}>
        Operational metrics only — no clinical interpretation (Feature 1.12).
      </p>

      <div className="grid-4" style={{ marginTop: 40 }}>
        <div className="card"><p className="label muted">Total cases</p><p className="dial-value" style={{ marginTop: 8 }}>{data.total_cases}</p></div>
        <div className="card"><p className="label muted">Last 7 days</p><p className="dial-value" style={{ marginTop: 8 }}>{data.cases_last_7_days}</p></div>
        <div className="card"><p className="label muted">Safety overrides</p><p className="dial-value" style={{ marginTop: 8, color: data.safety_override_cases ? "var(--danger)" : undefined }}>{data.safety_override_cases}</p></div>
        <div className="card"><p className="label muted">Demo cases</p><p className="dial-value" style={{ marginTop: 8 }}>{data.demonstration_data_usage}</p></div>
      </div>

      <div className="grid-2" style={{ marginTop: 40, alignItems: "start" }}>
        <div className="card">
          <h4 style={{ marginBottom: 16 }}>Cases by day</h4>
          {Object.entries(data.cases_by_day).map(([day, n]) => (
            <Bar key={day} label={day} value={n} max={maxDay} />
          ))}
          {Object.keys(data.cases_by_day).length === 0 && <p className="muted body-sm">No data yet.</p>}
        </div>

        <div className="card">
          <h4 style={{ marginBottom: 16 }}>Language distribution</h4>
          {Object.entries(data.language_distribution).map(([lang, n]) => (
            <Bar key={lang} label={lang.toUpperCase()} value={n} max={maxLang} />
          ))}
          <p className="caption" style={{ marginTop: 12 }}>
            Monitored for fairness disparities (Features 2.8 / 2.24).
          </p>
        </div>

        <div className="card">
          <h4 style={{ marginBottom: 16 }}>Priority distribution</h4>
          {Object.entries(data.priority_distribution).map(([band, n]) => (
            <Bar key={band} label={band} value={n} max={maxPrio} />
          ))}
        </div>

        <div className="card">
          <h4 style={{ marginBottom: 16 }}>AI vs human decisions</h4>
          <table className="data">
            <tbody>
              <tr><td>AI recommended (accepted)</td><td className="mono">{data.ai_vs_human_decisions.human_confirmed}</td></tr>
              <tr><td>Human overrode AI</td><td className="mono">{data.ai_vs_human_decisions.human_overrode}</td></tr>
              {Object.entries(data.ai_vs_human_decisions.by_decision).map(([k, v]) => (
                <tr key={k}><td className="muted">· {k}</td><td className="mono">{v}</td></tr>
              ))}
            </tbody>
          </table>
          <p className="caption" style={{ marginTop: 12 }}>Feature 2.21 — human-AI agreement tracking.</p>
        </div>

        <div className="card">
          <h4 style={{ marginBottom: 16 }}>Duration categories</h4>
          {Object.entries(data.duration_categories).map(([k, v]) => (
            <Bar key={k} label={k} value={v} max={Math.max(1, ...Object.values(data.duration_categories))} />
          ))}
        </div>

        <div className="card">
          <h4 style={{ marginBottom: 16 }}>Escalation trends</h4>
          {Object.entries(data.escalation_trends).map(([day, n]) => (
            <Bar key={day} label={day} value={n} max={Math.max(1, ...Object.values(data.escalation_trends))} />
          ))}
          {Object.keys(data.escalation_trends).length === 0 && <p className="muted body-sm">No escalations recorded.</p>}
        </div>
      </div>
    </div>
  );
}

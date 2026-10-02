import { useEffect, useState } from "react";
import { api } from "../api/client";
import { EmptyState, Loading, useToasts, Toasts } from "../components/ui";

const ACTIONS = ["", "login", "login_failed", "created", "case_access", "ai_analysis",
  "reviewed", "flag_modified", "escalated", "dismissed", "referral", "summary_generated",
  "deleted", "admin_change", "modified"];

export default function Audit() {
  const [entries, setEntries] = useState(null);
  const [action, setAction] = useState("");
  const { toasts, push, dismiss } = useToasts();

  useEffect(() => {
    api("/api/v1/audit", { params: { action, limit: 200 } })
      .then((d) => setEntries(d.entries))
      .catch((err) => { push(err.message, "danger"); setEntries([]); });
  }, [action, push]);

  if (!entries) return <div className="page"><Loading text="Loading audit trail" /></div>;

  return (
    <div className="page">
      <Toasts toasts={toasts} dismiss={dismiss} />
      <div className="row-between wrap" style={{ gap: 16 }}>
        <div>
          <h2>Audit trail.</h2>
          <p className="body-lg muted" style={{ marginTop: 8 }}>
            Every login, access, analysis, change, escalation and deletion (Feature 1.13).
          </p>
        </div>
        <select className="input" style={{ maxWidth: 240 }} value={action} onChange={(e) => setAction(e.target.value)}>
          {ACTIONS.map((a) => <option key={a} value={a}>{a || "All actions"}</option>)}
        </select>
      </div>

      <div className="card card-flush" style={{ marginTop: 32 }}>
        {entries.length === 0 ? (
          <div style={{ padding: 24 }}><EmptyState title="No entries." /></div>
        ) : (
          <div className="table-scroll"><table className="data">
            <thead>
              <tr><th>Action</th><th>Details</th><th>Case</th><th>User</th><th>Timestamp (UTC)</th></tr>
            </thead>
            <tbody>
              {entries.map((e) => (
                <tr key={e.id}>
                  <td><span className="pill pill-outline">{e.action}</span></td>
                  <td className="body-sm">{e.details}</td>
                  <td className="caption">{e.case_id ? e.case_id.slice(0, 8) : "—"}</td>
                  <td className="caption">{e.user_id ? e.user_id.slice(0, 8) : "—"}</td>
                  <td className="caption mono">{e.timestamp ? new Date(e.timestamp).toISOString().replace("T", " ").slice(0, 19) : ""}</td>
                </tr>
              ))}
            </tbody>
          </table></div>
        )}
      </div>
    </div>
  );
}

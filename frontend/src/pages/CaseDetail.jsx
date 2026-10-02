import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, getUser } from "../api/client";
import { can } from "../api/roles";
import FlagsPanel from "../components/FlagsPanel";
import { ProfilePanel, UncertaintyPanel } from "../components/ProfilePanel";
import {
  EmptyState, Loading, Modal, ScoreBar, StatusPill, Toasts, useToasts,
} from "../components/ui";

const REFERRAL_TYPES = [
  "counselling", "mental_health", "medical", "legal_aid",
  "protection", "emergency", "shelter", "rehabilitation", "welfare",
];

export default function CaseDetail() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const user = getUser();
  const { toasts, push, dismiss } = useToasts();

  const [data, setData] = useState(null);
  const [audit, setAudit] = useState(null);
  const [decision, setDecision] = useState("confirm");
  const [notes, setNotes] = useState("");
  const [noteBody, setNoteBody] = useState("");
  const [finalPriority, setFinalPriority] = useState(null);
  const [showReferral, setShowReferral] = useState(false);
  const [referral, setReferral] = useState({ referral_type: "counselling", notes: "" });
  const [assignable, setAssignable] = useState([]);
  const [dueAt, setDueAt] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const c = await api(`/api/v1/cases/${caseId}`);
      setData(c);
      setFinalPriority(c.review_priority_score);
      if (can(user.role, "audit_read")) {
        api(`/api/v1/cases/${caseId}/audit`).then((a) => setAudit(a.entries)).catch(() => {});
      }
    } catch (err) {
      push(err.message, "danger");
    }
  }, [caseId, push, user.role]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (can(user.role, "user_list")) {
      api("/api/v1/users/assignable").then(setAssignable).catch(() => {});
    }
  }, [user.role]);

  const act = async (fn, successMsg) => {
    setBusy(true);
    try {
      await fn();
      push(successMsg);
      await load();
    } catch (err) {
      push(err.message, "danger");
    } finally {
      setBusy(false);
    }
  };

  if (!data) return <div className="page"><Loading text="Loading case" /></div>;

  const override = data.safety_override;
  const closed = data.status === "closed";

  return (
    <div className="page">
      <Toasts toasts={toasts} dismiss={dismiss} />

      <div className="row-between wrap" style={{ gap: 16 }}>
        <div className="row wrap" style={{ gap: 12 }}>
          <h3>{data.case_number}</h3>
          <StatusPill status={data.status} />
          {override && <span className="pill pill-danger">Safety override</span>}
          {data.anonymized && <span className="pill pill-outline">anonymized</span>}
          {data.is_demo && <span className="pill pill-outline">demo</span>}
        </div>
        <div className="row wrap" style={{ gap: 8 }}>
          <Link className="btn btn-soft" to="/">← Queue</Link>
          {!closed && <Link className="btn btn-outline" to={`/session/${data.id}`}>Open live console</Link>}
        </div>
      </div>

      {override && (
        <div className="safety-banner" style={{ marginTop: 16 }}>
          <span className="pill pill-danger" style={{ height: 24 }}>SAFETY OVERRIDE</span>
          <span className="reason">{data.safety_override_reason}</span>
        </div>
      )}

      <div className="grid-2" style={{ marginTop: 24, alignItems: "start" }}>
        {/* LEFT — transcript, summary, notes */}
        <div className="col" style={{ gap: 16 }}>
          <div className="card">
            <div className="row-between" style={{ marginBottom: 12 }}>
              <h4>Transcript</h4>
              <span className="pill pill-outline">
                {((data.language_info?.primary || {}).language || "en").toUpperCase()}
                {data.language_info?.code_switching?.is_code_switched ? " · code-switched" : ""}
              </span>
            </div>
            {data.language_info?.code_switching?.is_code_switched && (
              <p className="caption" style={{ marginBottom: 10 }}>
                Language switches detected: {data.language_info.code_switching.languages_detected?.join(" → ")}.
                Switches are not treated as pauses/silence (Feature 2.9 / rules.md).
              </p>
            )}
            <div className="transcript" style={{ maxHeight: 360, overflowY: "auto" }}>
              {(data.transcript || []).length === 0 && <p className="muted body-sm">No transcript.</p>}
              {(data.transcript || []).map((l, i) => (
                <div key={i} className={`msg ${l.speaker === "operator" ? "msg-operator" : "msg-caller"}`}>
                  {l.text}
                  <div className="msg-meta">
                    <span className="caption" style={{ color: l.speaker === "operator" ? "#d0d0d0" : undefined }}>
                      t+{Number(l.timestamp || 0).toFixed(1)}s
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <div className="row-between" style={{ marginBottom: 12 }}>
              <h4>Summary</h4>
              {data.summary?.label && (
                <span className={`pill ${data.summary.generated_by === "ai" ? "pill-ink" : "pill-outline"}`}>
                  {data.summary.label}
                </span>
              )}
            </div>
            {!data.summary || !data.summary.verbatim_summary ? (
              <div className="row-between wrap" style={{ gap: 12 }}>
                <p className="body-sm muted">No summary generated yet.</p>
                <button className="btn btn-soft btn-sm" disabled={busy || closed}
                        onClick={() => act(() => api(`/api/v1/cases/${caseId}/summary`, { method: "POST" }), "Summary generated.")}>
                  Generate summary
                </button>
              </div>
            ) : (
              <div className="col" style={{ gap: 10 }}>
                <div>
                  <p className="label muted">What the caller said</p>
                  <p className="body-sm">{data.summary.verbatim_summary.user_statement || "—"}</p>
                </div>
                <div className="hairline-top" style={{ paddingTop: 10 }}>
                  <p className="label muted">AI inference</p>
                  <p className="body-sm">
                    Distress: <strong>{data.summary.ai_inference?.distress_level}</strong>
                    {data.summary.ai_inference?.potential_underlying_issue && (
                      <> · {data.summary.ai_inference.potential_underlying_issue}</>
                    )}
                  </p>
                </div>
                <details>
                  <summary className="caption">Extractive fallback</summary>
                  <pre className="body-sm" style={{ whiteSpace: "pre-wrap", marginTop: 6 }}>{data.summary.fallback_text}</pre>
                </details>
              </div>
            )}
          </div>

          <div className="card">
            <h4 style={{ marginBottom: 12 }}>Notes & timeline</h4>
            {!closed && (
              <div className="row" style={{ gap: 8, marginBottom: 12 }}>
                <input className="input body-sm" placeholder="Add a reviewer note…" value={noteBody}
                       onChange={(e) => setNoteBody(e.target.value)} />
                <button className="btn btn-soft" disabled={!noteBody.trim() || busy}
                        onClick={() => act(async () => {
                          await api(`/api/v1/cases/${caseId}/notes`, { method: "POST", body: { body: noteBody } });
                          setNoteBody("");
                        }, "Note added.")}>
                  Add
                </button>
              </div>
            )}
            <ul className="list-reset col" style={{ gap: 8 }}>
              {(data.notes || []).map((n) => (
                <li key={n.id} className="flag-card" style={{ padding: 12 }}>
                  <span className="body-sm">{n.body}</span>
                  <div className="caption" style={{ marginTop: 4 }}>{n.author} · {n.author_role} · {new Date(n.created_at).toLocaleString()}</div>
                </li>
              ))}
              {(data.followups || []).map((f) => {
                const overdue = f.due_at && !f.completed && String(f.due_at) <= new Date().toISOString().slice(0, 10);
                return (
                  <li key={f.id} className="flag-card" style={{ padding: 12, opacity: f.completed ? 0.7 : 1 }}>
                    <div className="row wrap" style={{ gap: 8 }}>
                      <span className="pill pill-outline">{f.stage}</span>
                      {f.due_at && (
                        <span className={`pill ${f.completed ? "pill-ok" : overdue ? "pill-danger" : "pill-outline"}`}>
                          {f.completed ? "done" : overdue ? "overdue" : `due ${f.due_at}`}
                        </span>
                      )}
                      <span className="body-sm">{f.note}</span>
                    </div>
                    <div className="row-between wrap" style={{ marginTop: 6, gap: 8 }}>
                      <span className="caption">{f.by} · {new Date(f.created_at).toLocaleString()}{f.outcome ? ` · ${f.outcome}` : ""}</span>
                      {!f.completed && !closed && can(user.role, "case_review") && (
                        <button className="btn btn-outline btn-sm" disabled={busy}
                                onClick={() => act(() => api(`/api/v1/cases/${caseId}/followups/${f.id}`, {
                                  method: "PATCH", body: { completed: true },
                                }), "Follow-up completed.")}>
                          Mark done
                        </button>
                      )}
                    </div>
                  </li>
                );
              })}
              {(data.notes || []).length === 0 && (data.followups || []).length === 0 && (
                <li className="caption">No notes yet.</li>
              )}
            </ul>
            {!closed && (
              <div className="row wrap" style={{ gap: 8, marginTop: 12 }}>
                <input type="date" className="input body-sm" style={{ maxWidth: 170 }}
                       value={dueAt} onChange={(e) => setDueAt(e.target.value)} aria-label="Due date" />
                {["intervention", "followup", "reassessment"].map((stage) => (
                  <button key={stage} className="btn btn-outline btn-sm" disabled={busy}
                          onClick={() => act(async () => {
                            await api(`/api/v1/cases/${caseId}/followups`, {
                              method: "POST",
                              body: { stage, note: `Stage: ${stage} recorded`, due_at: dueAt || null },
                            });
                            setDueAt("");
                          }, `Logged ${stage}${dueAt ? ` (due ${dueAt})` : ""}.`)}>
                    Log {stage}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT — score, assignment, human decision, profile, flags, referrals */}
        <div className="col" style={{ gap: 16 }}>
          <div className="card">
            <div className="row-between" style={{ marginBottom: 10 }}>
              <h4>Assignment</h4>
              <span className={`pill ${data.assigned_to ? "pill-outline" : "pill-ok"}`}>
                {data.assigned_to_username || "unassigned"}
              </span>
            </div>
            {closed ? (
              <p className="body-sm muted">Case closed — assignment frozen.</p>
            ) : can(user.role, "user_list") ? (
              <select className="input" value={data.assigned_to || ""}
                      onChange={(e) => act(() => api(`/api/v1/cases/${caseId}`, {
                        method: "PATCH", body: { assigned_to: e.target.value },
                      }), "Assignment updated.")}>
                <option value="">Unassigned</option>
                {assignable.map((u) => (
                  <option key={u.id} value={u.id}>{u.display_name} · {u.role}</option>
                ))}
              </select>
            ) : data.assigned_to === user.id ? (
              <p className="body-sm muted">Assigned to you.</p>
            ) : (
              <button className="btn btn-outline btn-sm"
                      disabled={busy || !!data.assigned_to}
                      title={data.assigned_to ? "Already assigned — a supervisor can reassign" : undefined}
                      onClick={() => act(() => api(`/api/v1/cases/${caseId}`, {
                        method: "PATCH", body: { assigned_to: user.id },
                      }), "Case assigned to you.")}>
                Assign to me
              </button>
            )}
            <p className="caption" style={{ marginTop: 8 }}>
              Assignment is supervisor/counsellor-led (operators may self-assign) and always audited.
            </p>
          </div>

          <div className="card">
            <div className="row-between" style={{ marginBottom: 8 }}>
              <div>
                <p className="label muted">Review Priority Score</p>
                <p className="caption">Operational only (Feature 1.4)</p>
              </div>
              <span className="dial-value mono" style={{ color: override ? "var(--danger)" : undefined }}>
                {Number(data.review_priority_score).toFixed(2)}
              </span>
            </div>
            <ScoreBar value={data.review_priority_score} danger={override} />

            {data.final_decision && (
              <div className="card-soft" style={{ marginTop: 14, padding: 14 }}>
                <div className="row-between">
                  <span className="label">Human decision</span>
                  <span className="pill pill-ink">{data.final_decision.decision}</span>
                </div>
                <p className="caption" style={{ marginTop: 6 }}>
                  by {data.final_decision.decided_by} ({data.final_decision.decided_role}) · score{" "}
                  {data.final_decision.original_score} → {data.final_decision.final_score}
                </p>
                {data.final_decision.notes && <p className="body-sm" style={{ marginTop: 6 }}>“{data.final_decision.notes}”</p>}
              </div>
            )}

            {!closed && can(user.role, "case_review") && (
              <div className="col" style={{ gap: 10, marginTop: 14 }}>
                <div className="row-between">
                  <span className="label">Human decision (Feature 1.6)</span>
                  <span className="caption">AI never decides</span>
                </div>
                <div className="row wrap" style={{ gap: 8 }}>
                  {["confirm", "modify", "escalate", "dismiss"].map((d) => (
                    <button
                      key={d}
                      className={`btn btn-sm ${decision === d ? "btn-primary" : "btn-outline"}`}
                      disabled={d === "escalate" && !can(user.role, "case_escalate")
                        || d === "dismiss" && override}
                      title={d === "dismiss" && override ? "Safety Override active — dismissal blocked" : undefined}
                      onClick={() => setDecision(d)}
                    >
                      {d}
                    </button>
                  ))}
                </div>
                {decision === "modify" && (
                  <label className="field">
                    <span>Adjusted priority: {Number(finalPriority).toFixed(2)}</span>
                    <input type="range" min="0" max="1" step="0.05" value={finalPriority ?? 0}
                           onChange={(e) => setFinalPriority(Number(e.target.value))} />
                  </label>
                )}
                <textarea className="input body-sm" rows={3} placeholder="Review notes…"
                          value={notes} onChange={(e) => setNotes(e.target.value)} />
                <button
                  className="btn btn-primary"
                  disabled={busy || (decision === "dismiss" && override)}
                  onClick={() => act(() => api(`/api/v1/cases/${caseId}/review`, {
                    method: "POST",
                    body: {
                      decision,
                      override_ai: false,
                      notes,
                      final_priority: decision === "modify" ? finalPriority : undefined,
                    },
                  }), "Decision recorded in audit trail.")}
                >
                  Record decision
                </button>
              </div>
            )}
          </div>

          <div className="card">
            <h4 style={{ marginBottom: 12 }}>Safety & wellbeing profile</h4>
            <ProfilePanel profile={data.victim_safety_profile} />
          </div>

          <UncertaintyPanel uncertainty={data.uncertainty} />

          <div className="card">
            <div className="row-between" style={{ marginBottom: 12 }}>
              <h4>Indicators</h4>
              <span className="pill pill-outline">explainable · evidence-linked</span>
            </div>
            <FlagsPanel caseId={caseId} flags={data.ai_flags} safetyOverride={override}
                        onUpdate={load} notify={push} />
          </div>

          <div className="card">
            <div className="row-between" style={{ marginBottom: 12 }}>
              <h4>Referrals</h4>
              {!closed && (
                <button className="btn btn-soft btn-sm" onClick={() => setShowReferral(true)}>New referral</button>
              )}
            </div>
            {(data.referrals || []).length === 0 ? (
              <p className="body-sm muted">No referrals. AI suggests pathways — humans confirm them (Feature 2.16).</p>
            ) : (
              <ul className="list-reset col" style={{ gap: 8 }}>
                {data.referrals.map((r) => (
                  <li key={r.id} className="row-between" style={{ border: "1px solid var(--hairline-soft)", borderRadius: 16, padding: "10px 14px" }}>
                    <div className="col" style={{ gap: 2 }}>
                      <strong className="body-sm">{r.referral_type}</strong>
                      <span className="caption">{r.ai_suggested ? "AI-suggested" : "human-initiated"}</span>
                    </div>
                    <div className="row" style={{ gap: 8 }}>
                      <span className={`pill ${r.status === "confirmed" ? "pill-ok" : "pill-outline"}`}>{r.status}</span>
                      {r.status === "pending" && can(user.role, "referral_confirm") && (
                        <button className="btn btn-outline btn-sm" disabled={busy}
                                onClick={() => act(() => api(`/api/v1/cases/${caseId}/referrals/${r.id}/confirm`, { method: "POST" }), "Referral confirmed.")}>
                          Confirm
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {!closed && can(user.role, "case_anonymize") && (
            <div className="card">
              <h4 style={{ marginBottom: 8 }}>Close case</h4>
              <p className="body-sm muted" style={{ marginBottom: 12 }}>
                Scrubs PII from transcript, notes and summary, then closes the case (Feature 1.10).
              </p>
              <button className="btn btn-outline" disabled={busy}
                      onClick={() => act(() => api(`/api/v1/cases/${caseId}/anonymize`, { method: "POST", body: {} }), "Case closed & anonymized.")}>
                Anonymize & close
              </button>
            </div>
          )}

          {audit && audit.length > 0 && (
            <div className="card card-flush">
              <div style={{ padding: "20px 24px 8px" }}><h4>Audit trail</h4></div>
              <div className="table-scroll" style={{ maxHeight: 300, overflowY: "auto" }}>
                <table className="data">
                  <thead>
                    <tr><th>Action</th><th>Details</th><th>When</th></tr>
                  </thead>
                  <tbody>
                    {audit.map((e) => (
                      <tr key={e.id}>
                        <td><span className="pill pill-outline">{e.action}</span></td>
                        <td className="body-sm">{e.details}</td>
                        <td className="caption">{e.timestamp ? new Date(e.timestamp).toLocaleString() : ""}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {showReferral && (
        <Modal title="New referral (human-confirmed)" onClose={() => setShowReferral(false)}>
          <div className="col" style={{ gap: 14 }}>
            <label className="field">
              <span>Pathway</span>
              <select className="input" value={referral.referral_type}
                      onChange={(e) => setReferral({ ...referral, referral_type: e.target.value })}>
                {REFERRAL_TYPES.map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
              </select>
            </label>
            <label className="field">
              <span>Notes</span>
              <textarea className="input body-sm" rows={3} value={referral.notes}
                        onChange={(e) => setReferral({ ...referral, notes: e.target.value })} />
            </label>
            <button className="btn btn-primary"
                    disabled={busy}
                    onClick={() => act(async () => {
                      await api(`/api/v1/cases/${caseId}/referrals`, { method: "POST", body: referral });
                      setShowReferral(false);
                      setReferral({ referral_type: "counselling", notes: "" });
                    }, "Referral created — pending confirmation.")}>
              Create referral
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

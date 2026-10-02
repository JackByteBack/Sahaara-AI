import { useState } from "react";
import { api } from "../api/client";
import { getUser } from "../api/client";
import { can } from "../api/roles";
import { SeverityPill } from "./ui";

const DECISIONS = [
  { key: "confirm", label: "Confirm", cls: "btn-soft" },
  { key: "modify", label: "Modify", cls: "btn-soft" },
  { key: "escalate", label: "Escalate", cls: "btn-outline" },
  { key: "dismiss", label: "Dismiss", cls: "btn-outline" },
];

/**
 * Explainable AI flags + human-in-the-loop actions (Features 1.5 & 1.6).
 * AI suggests; the human confirms / modifies / escalates / dismisses.
 */
export default function FlagsPanel({ caseId, flags, safetyOverride, onUpdate, notify }) {
  const user = getUser();
  const [busy, setBusy] = useState(null);
  const [notes, setNotes] = useState({});

  const decide = async (flag, decision) => {
    if (decision === "escalate" && !can(user.role, "case_escalate")) {
      notify?.("Escalation requires supervisor / counsellor role.", "danger");
      return;
    }
    setBusy(flag.id);
    try {
      await api(`/api/v1/cases/${caseId}/flags/${flag.id}/decision`, {
        method: "POST",
        body: { decision, notes: notes[flag.id] || "" },
      });
      notify?.(`Flag ${decision}ed.`);
      await onUpdate?.();
    } catch (err) {
      notify?.(err.message, "danger");
    } finally {
      setBusy(null);
    }
  };

  if (!flags?.length) {
    return <p className="muted body-sm">No indicators flagged yet. AI suggestions appear here as the conversation progresses.</p>;
  }

  return (
    <div className="col" style={{ gap: 12 }}>
      {flags.map((flag) => {
        const critical = ["immediate_danger", "self_harm"].includes(flag.category)
          && ["high", "critical"].includes(flag.severity);
        const dismissBlocked = critical && safetyOverride;
        const decided = flag.human_decision && flag.human_decision !== "modify";
        return (
          <div key={flag.id} className={`flag-card sev-${flag.severity}${decided ? " decided" : ""}`}>
            <div className="row-between">
              <div className="row wrap" style={{ gap: 8 }}>
                <span className="pill pill-ink">{flag.category.replace("_", " ")}</span>
                <SeverityPill severity={flag.severity} />
                <span className="caption">
                  confidence {(flag.confidence * 100).toFixed(0)}% · {flag.source} · t+{Number(flag.timestamp).toFixed(1)}s
                </span>
              </div>
              {flag.human_decision && (
                <span className={`pill ${flag.human_decision === "dismiss" ? "pill-outline" : "pill-ok"}`}>
                  human: {flag.human_decision}
                </span>
              )}
            </div>

            <p className="body-sm" style={{ marginTop: 8 }}>{flag.description}</p>

            <div className="flag-evidence" style={{ marginTop: 8 }}>
              “{flag.transcript_excerpt}”
            </div>

            {flag.alternatives_considered?.length > 0 && (
              <p className="caption" style={{ marginTop: 6 }}>
                Alternative explanations considered: {flag.alternatives_considered.join("; ")} (Feature 2.11)
              </p>
            )}

            {flag.decision_notes && <p className="caption" style={{ marginTop: 6 }}>Reviewer note: {flag.decision_notes}</p>}

            {!decided && can(user.role, "case_review") && (
              <div className="col" style={{ marginTop: 10, gap: 8 }}>
                <input
                  className="input body-sm"
                  placeholder="Optional reviewer note…"
                  value={notes[flag.id] || ""}
                  onChange={(e) => setNotes({ ...notes, [flag.id]: e.target.value })}
                />
                <div className="row wrap" style={{ gap: 8 }}>
                  {DECISIONS.map((d) => {
                    const blocked = busy === flag.id
                      || (d.key === "dismiss" && dismissBlocked)
                      || (d.key === "escalate" && !can(user.role, "case_escalate"));
                    return (
                      <button
                        key={d.key}
                        className={`btn btn-sm ${d.cls}`}
                        disabled={blocked}
                        title={
                          d.key === "dismiss" && dismissBlocked
                            ? "Safety Override active — this flag cannot be dismissed (rules.md)."
                            : d.key === "escalate" && !can(user.role, "case_escalate")
                              ? "Requires supervisor / counsellor role"
                              : undefined
                        }
                        onClick={() => decide(flag, d.key)}
                      >
                        {d.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

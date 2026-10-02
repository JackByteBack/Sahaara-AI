/**
 * Victim Safety & Wellbeing Profile (Feature 2.2) + uncertainty panel (2.10).
 * Deliberately shown next to — and labelled separately from — the operational
 * Review Priority Score (Decision 1: dual-layer assessment architecture).
 */

const DIMENSIONS = [
  ["psych_distress", "Psychological distress"],
  ["trauma_indicators", "Trauma indicators"],
  ["immediate_danger", "Immediate danger"],
  ["self_harm", "Self-harm concern"],
  ["intimidation_coercion", "Intimidation / coercion"],
  ["social_vulnerability", "Social vulnerability"],
  ["medical_vulnerability", "Medical vulnerability"],
  ["legal_service_vulnerability", "Legal / service vulnerability"],
];

const LEVEL_TONE = {
  CRITICAL: "pill-danger",
  HIGH: "pill-danger",
  POSSIBLE: "pill-warn",
  MODERATE: "pill-warn",
  LOW: "pill",
  UNKNOWN: "pill-outline",
};

function LevelPill({ level }) {
  return <span className={`pill ${LEVEL_TONE[level] || "pill-outline"}`}>{level || "UNKNOWN"}</span>;
}

export function ProfilePanel({ profile }) {
  if (!profile || !profile.assessed_dimensions) {
    return <p className="muted body-sm">Profile builds as indicators are detected.</p>;
  }
  return (
    <div className="col" style={{ gap: 10 }}>
      {DIMENSIONS.map(([key, label]) => {
        const dim = profile[key] || { level: "UNKNOWN", confidence: 0, evidence: [] };
        return (
          <div key={key} className="row-between" style={{ alignItems: "flex-start" }}>
            <div className="col" style={{ gap: 4 }}>
              <span className="body-sm" style={{ fontWeight: 600 }}>{label}</span>
              {dim.evidence?.length > 0 && (
                <span className="caption">“{dim.evidence[0]}”</span>
              )}
            </div>
            <div className="col" style={{ alignItems: "flex-end", gap: 2 }}>
              <LevelPill level={dim.level} />
              {dim.confidence > 0 && <span className="caption mono">{(dim.confidence * 100).toFixed(0)}%</span>}
            </div>
          </div>
        );
      })}
      <p className="caption" style={{ marginTop: 4 }}>{profile.note}</p>
    </div>
  );
}

export function UncertaintyPanel({ uncertainty }) {
  if (!uncertainty || !uncertainty.evidence_quality) return null;
  return (
    <div className="card-soft" style={{ padding: 16 }}>
      <div className="row-between">
        <span className="label">Assessment confidence</span>
        <span className="pill pill-outline mono">
          {Number(uncertainty.assessment_confidence || 0).toFixed(2)}
        </span>
      </div>
      <div className="row-between" style={{ marginTop: 8 }}>
        <span className="label">Evidence quality</span>
        <span className="pill">{uncertainty.evidence_quality}</span>
      </div>
      {uncertainty.missing_information?.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <span className="label">Missing information</span>
          <ul className="list-reset" style={{ marginTop: 4 }}>
            {uncertainty.missing_information.map((m) => (
              <li key={m} className="caption">• {m}</li>
            ))}
          </ul>
        </div>
      )}
      <p className="caption" style={{ marginTop: 8 }}>
        Recommended action: <strong>{String(uncertainty.recommended_action).replace(/_/g, " ")}</strong>
      </p>
    </div>
  );
}

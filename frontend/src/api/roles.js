/* Client-side RBAC mirror of backend/app/deps.py (Feature 1.11). */
export const CAPABILITIES = {
  case_read: ["admin", "operator", "supervisor", "counsellor"],
  case_create: ["admin", "operator", "supervisor"],
  case_review: ["admin", "operator", "supervisor", "counsellor"],
  case_escalate: ["admin", "supervisor", "counsellor"],
  referral_confirm: ["admin", "supervisor", "counsellor"],
  case_anonymize: ["admin", "supervisor"],
  analytics_read: ["admin", "supervisor", "counsellor", "operator"],
  audit_read: ["admin", "supervisor"],
  user_manage: ["admin"],
  user_list: ["admin", "supervisor", "counsellor"],
};

export function can(role, capability) {
  return (CAPABILITIES[capability] || []).includes(role);
}

export const ROLE_LABELS = {
  admin: "Administrator",
  supervisor: "Supervisor",
  counsellor: "Counsellor / Reviewer",
  operator: "Operator",
};

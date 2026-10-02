import { useEffect, useState } from "react";

/* ── Small shared UI atoms (DESIGN.md component language) ───────────── */

export function ScoreBar({ value, danger }) {
  const pct = Math.round((value || 0) * 100);
  return (
    <div className="row" style={{ gap: 10 }}>
      <div className="score-track" style={{ flex: 1 }}>
        <div className={`score-fill${danger ? " danger" : ""}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="label mono" style={{ minWidth: 34, textAlign: "right" }}>{pct}</span>
    </div>
  );
}

const STATUS_STYLE = {
  active: "pill-outline",
  reviewing: "pill-ink",
  referred: "pill-warn",
  closed: "pill",
};

export function StatusPill({ status }) {
  return <span className={`pill ${STATUS_STYLE[status] || "pill"}`}>{status}</span>;
}

export function SeverityPill({ severity }) {
  const map = { critical: "pill-danger", high: "pill-danger", medium: "pill-warn", low: "pill" };
  return <span className={`pill ${map[severity] || "pill"}`}>{severity}</span>;
}

export function EmptyState({ title, subtitle, action }) {
  return (
    <div className="empty">
      <h4>{title}</h4>
      {subtitle && <p className="muted" style={{ marginTop: 8 }}>{subtitle}</p>}
      {action && <div style={{ marginTop: 16 }}>{action}</div>}
    </div>
  );
}

export function Modal({ title, onClose, children }) {
  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="row-between" style={{ marginBottom: 16 }}>
          <h4>{title}</h4>
          <button className="btn btn-soft btn-sm" onClick={onClose}>Close</button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function Segmented({ options, value, onChange }) {
  return (
    <div className="segmented">
      {options.map((opt) => (
        <button
          key={opt.value}
          className={value === opt.value ? "active" : ""}
          onClick={() => onChange(opt.value)}
          type="button"
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export function Toasts({ toasts, dismiss }) {
  return (
    <div className="toast-wrap">
      {toasts.map((t) => (
        <div key={t.id} className={`toast${t.tone === "danger" ? " danger" : ""}`} onClick={() => dismiss(t.id)}>
          {t.text}
        </div>
      ))}
    </div>
  );
}

export function useToasts() {
  const [toasts, setToasts] = useState([]);
  const push = (text, tone) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, text, tone }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4200);
  };
  const dismiss = (id) => setToasts((prev) => prev.filter((t) => t.id !== id));
  return { toasts, push, dismiss };
}

export function Loading({ text = "Loading…" }) {
  const [dots, setDots] = useState("");
  useEffect(() => {
    const t = setInterval(() => setDots((d) => (d.length >= 3 ? "" : d + ".")), 350);
    return () => clearInterval(t);
  }, []);
  return <p className="muted">{text}{dots}</p>;
}

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

/* Read-state lives in localStorage (client-side only — the feed itself is
   always derived fresh and stores nothing new about callers). */
const READ_KEY = "sahaara_notifications_read";

function readSet() {
  try {
    return JSON.parse(localStorage.getItem(READ_KEY) || "{}");
  } catch {
    return {};
  }
}

function markRead(id) {
  const set = readSet();
  set[id] = Date.now();
  localStorage.setItem(READ_KEY, JSON.stringify(set));
}

const SEV_COLOR = {
  critical: "var(--danger)",
  high: "var(--warn)",
  medium: "var(--primary)",
  low: "var(--text-faint)",
};

export default function NotificationBell() {
  const [items, setItems] = useState([]);
  const [open, setOpen] = useState(false);
  const [version, setVersion] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    let alive = true;
    const load = () =>
      api("/api/v1/notifications")
        .then((d) => alive && setItems(d.notifications || []))
        .catch(() => {});
    load();
    const iv = setInterval(load, 60000);
    return () => { alive = false; clearInterval(iv); };
  }, []);

  const read = readSet();
  const unread = items.filter((n) => !read[n.id]);

  const markAll = () => {
    items.forEach((n) => markRead(n.id));
    setVersion((v) => v + 1);
  };

  const openItem = (n) => {
    markRead(n.id);
    setVersion((v) => v + 1);
    setOpen(false);
    navigate(n.link);
  };

  return (
    <div style={{ position: "relative" }}>
      <button
        className="btn btn-soft btn-sm"
        style={{ padding: "0 10px", position: "relative" }}
        onClick={() => setOpen((o) => !o)}
        title="Notifications"
        aria-label={`Notifications (${unread.length} unread)`}
        key={version}
      >
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
          <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
          <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
        </svg>
        {unread.length > 0 && (
          <span
            style={{
              position: "absolute", top: -5, right: -5, minWidth: 17, height: 17,
              borderRadius: "999px", background: "var(--danger)", color: "#fff",
              fontSize: 10, fontWeight: 700, display: "inline-flex",
              alignItems: "center", justifyContent: "center", padding: "0 4px",
            }}
          >
            {unread.length > 9 ? "9+" : unread.length}
          </span>
        )}
      </button>

      {open && (
        <>
          <div style={{ position: "fixed", inset: 0, zIndex: 90 }} onClick={() => setOpen(false)} />
          <div
            className="card"
            style={{
              position: "absolute", right: 0, top: "calc(100% + 10px)", zIndex: 95,
              width: "min(360px, calc(100vw - 48px))", padding: 0, overflow: "hidden",
              maxHeight: 460, display: "flex", flexDirection: "column",
            }}
          >
            <div className="row-between" style={{ padding: "12px 14px", borderBottom: "1px solid var(--hairline-soft)" }}>
              <strong className="body-sm">Notifications</strong>
              <button className="btn btn-soft btn-sm" onClick={markAll}>Mark all read</button>
            </div>
            <div style={{ overflowY: "auto" }}>
              {items.length === 0 && (
                <p className="caption" style={{ padding: 16 }}>Nothing needs attention right now.</p>
              )}
              {items.map((n) => (
                <button
                  key={n.id}
                  onClick={() => openItem(n)}
                  style={{
                    display: "flex", gap: 10, width: "100%", textAlign: "left",
                    padding: "11px 14px", background: "transparent", border: "none",
                    borderBottom: "1px solid var(--hairline-soft)", cursor: "pointer",
                    fontFamily: "var(--font)", alignItems: "flex-start",
                    opacity: read[n.id] ? 0.6 : 1,
                  }}
                >
                  <span className="dot" style={{ background: SEV_COLOR[n.severity] || "var(--text-faint)", marginTop: 6, flexShrink: 0 }} />
                  <span style={{ minWidth: 0 }}>
                    <span className="body-sm" style={{ fontWeight: 600 }}>{n.title}</span>{" "}
                    <span className="caption">{n.case_number}</span>
                    <p className="caption" style={{ marginTop: 2 }}>{n.body}</p>
                  </span>
                </button>
              ))}
            </div>
            <p className="caption" style={{ padding: "8px 14px", borderTop: "1px solid var(--hairline-soft)" }}>
              Derived feed — safety overrides, due follow-ups, pending referrals, assignments.
            </p>
          </div>
        </>
      )}
    </div>
  );
}

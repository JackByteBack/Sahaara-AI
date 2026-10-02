import { NavLink, useNavigate } from "react-router-dom";
import { clearSession, getUser } from "../api/client";
import { ROLE_LABELS } from "../api/roles";
import NotificationBell from "./NotificationBell";

/* Floating, horizontally-centered nav pill (DESIGN.md nav-pill). */
export default function NavPill() {
  const user = getUser();
  const navigate = useNavigate();

  const logout = () => {
    clearSession();
    navigate("/login");
  };

  return (
    <nav className="nav-pill">
      <span className="nav-brand">
        <span
          aria-hidden
          style={{
            width: 26, height: 26, borderRadius: "30%", background: "var(--primary)",
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            color: "#fff", fontSize: 13, fontWeight: 650,
          }}
        >
          S
        </span>
        Sahaara AI
      </span>

      <div className="nav-links">
        <NavLink to="/" end>Queue</NavLink>
        <NavLink to="/cases" className="hide-mobile">Cases</NavLink>
        <NavLink to="/analytics" className="hide-mobile">Analytics</NavLink>
        {user && (user.role === "admin" || user.role === "supervisor") && (
          <NavLink to="/audit" className="hide-mobile">Audit</NavLink>
        )}
      </div>

      <div className="row" style={{ gap: 8 }}>
        <NotificationBell />
        <NavLink to="/settings" title="Settings" aria-label="Settings"
                 style={{ textDecoration: "none", fontSize: 15, padding: "6px 8px", borderRadius: 999 }}>
          ⚙
        </NavLink>
        {user && (
          <span className="pill pill-outline hide-mobile" title={`${user.display_name} · ${ROLE_LABELS[user.role]}`}>
            <span className="truncate" style={{ maxWidth: 150 }}>{user.display_name} · {user.role}</span>
          </span>
        )}
        <button className="btn btn-primary" onClick={logout}>Log out</button>
      </div>
    </nav>
  );
}

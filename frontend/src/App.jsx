import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import NavPill from "./components/NavPill";
import ErrorBoundary from "./components/ErrorBoundary";
import { getToken } from "./api/client";
import { useSafeExit } from "./hooks/useSafeExit";
import Login from "./pages/Login";
import Landing from "./pages/Landing";
import About from "./pages/About";
import Privacy from "./pages/Privacy";
import Terms from "./pages/Terms";
import Contact from "./pages/Contact";
import NotFound from "./pages/NotFound";
import ServerError from "./pages/ServerError";
import Dashboard from "./pages/Dashboard";
import Session from "./pages/Session";
import Cases from "./pages/Cases";
import CaseDetail from "./pages/CaseDetail";
import Analytics from "./pages/Analytics";
import Audit from "./pages/Audit";
import Settings from "./pages/Settings";

function RequireAuth({ children }) {
  if (!getToken()) return <Navigate to="/login" replace />;
  return children;
}

/** `/` shows the public landing page when logged out, the queue when logged in. */
function IndexRoute() {
  return getToken() ? <Dashboard /> : <Landing />;
}

/* Marketing/legal/error pages render their own header + footer (no app nav pill). */
const APP_PREFIXES = ["/session", "/cases", "/analytics", "/audit"];

export default function App() {
  const location = useLocation();
  const { arming, exitNow } = useSafeExit();
  const path = location.pathname;
  const authed = !!getToken();
  /* App chrome (nav pill + safe-exit) only on authenticated console screens. */
  const isAppScreen =
    authed &&
    (path === "/" || APP_PREFIXES.some((p) => path === p || path.startsWith(`${p}/`)));

  return (
    <ErrorBoundary>
      {isAppScreen && <NavPill />}
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<IndexRoute />} />
        <Route path="/about" element={<About />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/500" element={<ServerError />} />
        <Route path="/session/:caseId" element={<RequireAuth><Session /></RequireAuth>} />
        <Route path="/cases" element={<RequireAuth><Cases /></RequireAuth>} />
        <Route path="/cases/:caseId" element={<RequireAuth><CaseDetail /></RequireAuth>} />
        <Route path="/analytics" element={<RequireAuth><Analytics /></RequireAuth>} />
        <Route path="/audit" element={<RequireAuth><Audit /></RequireAuth>} />
        <Route path="/settings" element={<RequireAuth><Settings /></RequireAuth>} />
        <Route path="*" element={<NotFound />} />
      </Routes>

      {/* Feature 2.23 — discreet safe-exit affordance (double-Escape), app screens only */}
      {isAppScreen && (
        <button
          onClick={exitNow}
          title="Safe exit (or press Escape twice)"
          style={{
            position: "fixed", right: 14, bottom: 14, zIndex: 300,
            width: 40, height: 40, borderRadius: "30%", border: "1px solid var(--hairline)",
            background: "var(--canvas-soft)", color: "var(--text-muted)", cursor: "pointer", fontSize: 14,
          }}
        >
          ✕
        </button>
      )}
      {arming && (
        <div className="toast-wrap">
          <div className="toast danger">Press Escape again to exit safely.</div>
        </div>
      )}
    </ErrorBoundary>
  );
}

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, setSession } from "../api/client";
import { useSeo } from "../lib/seo";

const DEMO_ACCOUNTS = [
  ["operator", "operator123"],
  ["counsellor", "counsel123"],
  ["supervisor", "super123"],
  ["admin", "admin123"],
];

export default function Login() {
  useSeo({
    title: "Log in — Sahaara AI",
    description: "Sign in to the Sahaara AI helpline console.",
    path: "/login",
  });
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  const submit = async (e, u, p) => {
    e?.preventDefault();
    setBusy(true);
    setError("");
    try {
      const res = await api("/api/v1/auth/login", {
        method: "POST",
        body: { username: u ?? username, password: p ?? password },
      });
      setSession(res.access_token, res.user);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page page-narrow" style={{ paddingTop: 80 }}>
      <div style={{ maxWidth: 440, margin: "0 auto" }}>
        <div className="row" style={{ gap: 10, marginBottom: 28 }}>
          <span
            aria-hidden
            style={{
              width: 44, height: 44, borderRadius: "30%", background: "var(--primary)",
              display: "inline-flex", alignItems: "center", justifyContent: "center",
              color: "#fff", fontSize: 22, fontWeight: 650,
            }}
          >
            S
          </span>
          <div>
            <h3>Sahaara AI</h3>
            <p className="caption">Helpline decision support. AI advises — humans decide.</p>
          </div>
        </div>

        <div className="card-soft">
          <form onSubmit={submit} className="col" style={{ gap: 16 }}>
            <label className="field">
              <span>Username</span>
              <input className="input" autoFocus value={username}
                     onChange={(e) => setUsername(e.target.value)} placeholder="operator" />
            </label>
            <label className="field">
              <span>Password</span>
              <input className="input" type="password" value={password}
                     onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </label>
            {error && <p className="body-sm" style={{ color: "var(--danger)" }}>{error}</p>}
            <button className="btn btn-primary btn-lg" disabled={busy || !username || !password}>
              {busy ? "Signing in…" : "Continue"}
            </button>
          </form>
        </div>

        <p className="caption" style={{ marginTop: 20 }}>Demo accounts (click to sign in):</p>
        <div className="row wrap" style={{ marginTop: 8, gap: 8 }}>
          {DEMO_ACCOUNTS.map(([u, p]) => (
            <button key={u} className="btn btn-outline btn-sm" onClick={(e) => submit(e, u, p)}>
              {u}
            </button>
          ))}
        </div>

        <div className="card" style={{ marginTop: 28 }}>
          <p className="body-sm muted">
            <strong style={{ color: "var(--ink)" }}>Decision-support only.</strong> Sahaara identifies observable
            indicators and prioritises human review — it never diagnoses and never acts autonomously.
            Consent-first processing; raw audio is not retained by default.
          </p>
        </div>

        <div className="row wrap" style={{ marginTop: 24, gap: 16, justifyContent: "center" }}>
          <Link to="/" className="caption" style={{ textDecoration: "none" }}>Overview</Link>
          <Link to="/about" className="caption" style={{ textDecoration: "none" }}>About us</Link>
          <Link to="/privacy" className="caption" style={{ textDecoration: "none" }}>Privacy</Link>
          <Link to="/terms" className="caption" style={{ textDecoration: "none" }}>Terms</Link>
          <Link to="/contact" className="caption" style={{ textDecoration: "none" }}>Contact</Link>
        </div>
      </div>
    </div>
  );
}

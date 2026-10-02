import { Link } from "react-router-dom";

/* Public-site header: compact pill mirroring the app's nav-pill geometry. */
export function SiteHeader() {
  return (
    <header className="site-header">
      <nav className="nav-pill" style={{ position: "static", transform: "none", maxWidth: 1080, width: "100%" }}>
        <Link to="/" className="nav-brand" style={{ textDecoration: "none" }}>
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
        </Link>
        <div className="nav-links">
          <Link to="/about">About</Link>
          <Link to="/contact" className="hide-mobile">Contact</Link>
          <Link to="/privacy" className="hide-mobile">Privacy</Link>
        </div>
        <div className="row" style={{ gap: 8 }}>
          <Link to="/login" className="btn btn-outline btn-sm">Log in</Link>
          <Link to="/" className="btn btn-primary btn-sm">Open app</Link>
        </div>
      </nav>
    </header>
  );
}

/* Full-width near-black footer with rounded top corners (DESIGN.md `footer`). */
export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <div className="footer-brand">
          <p className="footer-wordmark">Sahaara.</p>
          <p className="body-sm" style={{ color: "var(--text-faint)", maxWidth: 420, marginTop: 12 }}>
            AI-assisted distress assessment and case management for helplines.
            The system advises — trained humans always decide.
          </p>
        </div>

        <div className="footer-cols">
          <div className="footer-col">
            <p className="label">Product</p>
            <Link to="/">Overview</Link>
            <Link to="/about">About us</Link>
            <Link to="/login">Log in</Link>
          </div>
          <div className="footer-col">
            <p className="label">Resources</p>
            <Link to="/#faq">FAQ</Link>
            <Link to="/contact">Contact us</Link>
          </div>
          <div className="footer-col">
            <p className="label">Legal</p>
            <Link to="/privacy">Privacy policy</Link>
            <Link to="/terms">Terms &amp; conditions</Link>
          </div>
        </div>
      </div>
      <div className="footer-base">
        <span className="caption" style={{ color: "var(--text-faint)" }}>
          © {new Date().getFullYear()} Sahaara AI. Decision-support only — not a diagnostic or emergency service.
        </span>
        <span className="caption" style={{ color: "var(--text-faint)" }}>
          In an emergency, contact local emergency services immediately.
        </span>
      </div>
    </footer>
  );
}

/** Standard legal/content page shell. */
export function ContentPage({ children }) {
  return (
    <div className="site-page">
      <SiteHeader />
      <main className="page page-narrow" style={{ paddingTop: 40 }}>
        {children}
      </main>
      <SiteFooter />
    </div>
  );
}

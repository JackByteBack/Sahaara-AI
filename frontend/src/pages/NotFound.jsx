import { Link } from "react-router-dom";
import { SiteFooter, SiteHeader } from "../components/SiteChrome";
import { useSeo } from "../lib/seo";

export default function NotFound() {
  useSeo({
    title: "Page Not Found (404) — Sahaara AI",
    description: "The page you were looking for does not exist.",
    path: "/404",
  });

  return (
    <div className="site-page">
      <SiteHeader />
      <main className="error-page">
        <p className="error-code">404</p>
        <h1>This page left the queue.</h1>
        <p className="body-lg muted" style={{ marginTop: 12, maxWidth: 460 }}>
          The link may be outdated, or the page may have moved. Nothing was harmed —
          you can head back to the overview.
        </p>
        <div className="row wrap" style={{ gap: 12, marginTop: 28, justifyContent: "center" }}>
          <Link to="/" className="btn btn-primary btn-lg">Back to overview</Link>
          <Link to="/contact" className="btn btn-outline btn-lg">Contact us</Link>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}

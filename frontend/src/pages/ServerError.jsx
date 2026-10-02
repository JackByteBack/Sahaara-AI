import { Link } from "react-router-dom";
import { SiteFooter, SiteHeader } from "../components/SiteChrome";
import { useSeo } from "../lib/seo";

export default function ServerError({ detail }) {
  useSeo({
    title: "Something Went Wrong (500) — Sahaara AI",
    description: "An unexpected error occurred.",
    path: "/500",
  });

  return (
    <div className="site-page">
      <SiteHeader />
      <main className="error-page">
        <p className="error-code">500</p>
        <h1>Something went wrong on our side.</h1>
        <p className="body-lg muted" style={{ marginTop: 12, maxWidth: 480 }}>
          The console hit an unexpected error. Your session data was not changed —
          reload to try again.
        </p>
        {detail && (
          <pre className="error-detail">{String(detail)}</pre>
        )}
        <div className="row wrap" style={{ gap: 12, marginTop: 28, justifyContent: "center" }}>
          <button className="btn btn-primary btn-lg" onClick={() => window.location.reload()}>
            Reload
          </button>
          <Link to="/" className="btn btn-outline btn-lg">Back to overview</Link>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}

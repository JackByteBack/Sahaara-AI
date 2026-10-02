import { useEffect } from "react";

const ORIGIN = "https://sahaara.ai";

function upsertMeta(selector, attr, key, content) {
  if (!content) return;
  let el = document.head.querySelector(selector);
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(attr, key);
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

/**
 * Client-side SEO: per-page title, meta description, canonical and Open Graph.
 * Crawlers without JS still receive the full base tags from index.html.
 */
export function useSeo({ title, description, path, image }) {
  useEffect(() => {
    if (title) document.title = title;

    upsertMeta('meta[name="description"]', "name", "description", description);
    upsertMeta('meta[property="og:title"]', "property", "og:title", title);
    upsertMeta('meta[property="og:description"]', "property", "og:description", description);
    upsertMeta('meta[property="og:url"]', "property", "og:url", `${ORIGIN}${path || ""}`);
    upsertMeta('meta[name="twitter:title"]', "name", "twitter:title", title);
    upsertMeta('meta[name="twitter:description"]', "name", "twitter:description", description);
    if (image) upsertMeta('meta[property="og:image"]', "property", "og:image", image);

    let canonical = document.head.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement("link");
      canonical.rel = "canonical";
      document.head.appendChild(canonical);
    }
    canonical.href = `${ORIGIN}${path || ""}`;
  }, [title, description, path, image]);
}

/** Inject a JSON-LD script block (removed on unmount). */
export function useJsonLd(data) {
  useEffect(() => {
    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.textContent = JSON.stringify(data);
    script.setAttribute("data-page-ld", "1");
    document.head.appendChild(script);
    return () => script.remove();
  }, [JSON.stringify(data)]);
}

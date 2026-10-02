/* API client — token kept in sessionStorage (data minimization, Feature 1.10). */

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8010";
export const WS_BASE = API_BASE.replace(/^http/, "ws");

export const TOKEN_KEY = "sahaara_token";
export const USER_KEY = "sahaara_user";

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}
export function getUser() {
  try {
    return JSON.parse(sessionStorage.getItem(USER_KEY) || "null");
  } catch {
    return null;
  }
}
export function setSession(token, user) {
  sessionStorage.setItem(TOKEN_KEY, token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(user));
}
export function clearSession() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
}

export class ApiError extends Error {
  constructor(status, detail) {
    super(typeof detail === "string" ? detail : JSON.stringify(detail));
    this.status = status;
    this.detail = detail;
  }
}

export async function api(path, { method = "GET", body, params } = {}) {
  const url = new URL(API_BASE + path);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, v);
    });
  }
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(url, { method, headers, body: body ? JSON.stringify(body) : undefined });
  if (res.status === 401) {
    clearSession();
    if (!window.location.pathname.startsWith("/login")) window.location.href = "/login";
    throw new ApiError(401, "Session expired");
  }
  let data = null;
  try {
    data = await res.json();
  } catch {
    /* no body */
  }
  if (!res.ok) {
    const detail = data?.detail?.[0]?.msg || data?.detail || res.statusText;
    throw new ApiError(res.status, detail);
  }
  return data;
}

/* Audited file export — fetches with the session token and triggers a download. */
export async function download(path, filename) {
  const res = await fetch(API_BASE + path, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch { /* no body */ }
    throw new ApiError(res.status, detail);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

/* Feature 2.23 — Safe Exit: wipe local traces and jump to a neutral page. */
export function safeExit() {
  try {
    sessionStorage.clear();
    localStorage.clear();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText("").catch(() => {});
    }
    if (window.indexedDB && window.indexedDB.databases) {
      window.indexedDB.databases().then((dbs) => dbs.forEach((d) => window.indexedDB.deleteDatabase(d.name))).catch(() => {});
    }
    document.cookie.split(";").forEach((c) => {
      const name = c.split("=")[0].trim();
      document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
    });
  } catch {
    /* best effort */
  }
  window.location.replace("https://www.google.com/search?q=weather");
}

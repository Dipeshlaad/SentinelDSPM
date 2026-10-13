export const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
// "Remember me" keeps the token in localStorage (survives closing the browser); otherwise it lives in sessionStorage.
export const tok = {
  get: () => sessionStorage.getItem("token") || localStorage.getItem("token"),
  set: (t: string, remember = false) => { tok.clear(); (remember ? localStorage : sessionStorage).setItem("token", t); },
  clear: () => { sessionStorage.removeItem("token"); localStorage.removeItem("token"); },
};
export function jwt(t: string | null): any {
  try { return JSON.parse(atob(t!.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))); } catch { return null; }
}
// NOTE: collection routes keep their trailing slash (FastAPI would otherwise redirect and drop CORS headers).
export async function api(path: string, o: { method?: string; body?: any; raw?: boolean } = {}): Promise<any> {
  const t = tok.get();
  let r: Response;
  try {
    r = await fetch(BASE + path, {
      method: o.method || "GET",
      headers: { ...(o.body ? { "Content-Type": "application/json" } : {}), ...(t ? { Authorization: `Bearer ${t}` } : {}) },
      body: o.body ? JSON.stringify(o.body) : undefined,
    });
  } catch {
    // A crashed request (HTTP 500) has no CORS headers, so the browser reports it as a network failure.
    throw new Error("Could not get a response from the server. If the backend is running, it hit an internal error: check its log for details.");
  }
  if (r.status === 401 && !path.includes("/auth/login")) { tok.clear(); location.href = "/login"; }
  if (!r.ok) {
    let d: any = r.statusText;
    try { d = (await r.json()).detail; } catch {}
    throw new Error(Array.isArray(d) ? d.map((x: any) => x.msg).join("; ") : String(d));
  }
  return o.raw ? r : r.json();
}

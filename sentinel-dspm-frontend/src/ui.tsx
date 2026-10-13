import { useCallback, useEffect, useState, ReactNode } from "react";
import { Moon, Sun, Loader2 } from "lucide-react";
import { api } from "./api";

export function useLoad(path: string | null, initial: any = null) {
  const [data, setData] = useState<any>(initial), [loading, setL] = useState(true), [err, setErr] = useState("");
  const load = useCallback(() => {
    if (!path) return;
    setL(true); setErr("");
    api(path).then(setData).catch((e) => setErr(e.message)).finally(() => setL(false));
  }, [path]);
  useEffect(load, [load]);
  return { data, loading, err, reload: load };
}

export const TYPES: Record<string, string> = {
  credit_card: "Credit card", aws_access_key: "AWS access key", aadhaar: "Aadhaar", pan: "PAN", email: "Email", phone: "Phone",
};
const C: Record<string, string> = {
  critical: "bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-500/15 dark:text-orange-300",
  medium: "bg-amber-100 text-amber-800 dark:bg-amber-500/15 dark:text-amber-300",
  low: "bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300",
  ok: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300",
};
const MAP: Record<string, string> = { none: "ok", resolved: "ok", completed: "ok", verified: "ok", active: "ok", open: "critical", failed: "critical", acknowledged: "medium", running: "low", pending: "low" };
export const Badge = ({ v }: { v: string }) => {
  const k = String(v || "").toLowerCase();
  return <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${C[MAP[k] || k] || "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300"}`}>{TYPES[k] || v}</span>;
};
export const fmt = (d?: string) => (d ? new Date(d).toLocaleString() : "—");
export const Spinner = () => <Loader2 className="h-4 w-4 animate-spin" />;
export const Err = ({ m }: { m?: string }) => (m ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{m}</p> : null);
export const Head = ({ title, sub, children }: { title: string; sub?: string; children?: ReactNode }) => (
  <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
    <div><h1 className="text-2xl font-semibold tracking-tight">{title}</h1>{sub && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{sub}</p>}</div>
    <div className="flex gap-2">{children}</div>
  </div>
);
export const Async = ({ l, children }: { l: any; children: ReactNode }) =>
  l.loading && !l.data ? <div className="flex justify-center p-10"><Spinner /></div> : l.err ? <div className="card"><Err m={l.err} /></div> : <>{children}</>;
export const Empty = ({ t }: { t: string }) => <p className="p-8 text-center text-sm text-slate-500">{t}</p>;
export const Table = ({ head, children, empty }: { head: string[]; children: ReactNode; empty?: string }) => (
  <div className="card overflow-x-auto p-0">
    <table className="w-full min-w-[640px]"><thead><tr>{head.map((h) => <th key={h} className="th">{h}</th>)}</tr></thead><tbody>{children}</tbody></table>
    {empty && <Empty t={empty} />}
  </div>
);
export function ThemeToggle() {
  const [dark, setDark] = useState(document.documentElement.classList.contains("dark"));
  return (
    <button className="btn2" aria-label="Toggle light or dark theme" onClick={() => {
      const n = !dark; setDark(n);
      document.documentElement.classList.toggle("dark", n); localStorage.theme = n ? "dark" : "light";
    }}>{dark ? <Sun size={16} /> : <Moon size={16} />}{dark ? "Light" : "Dark"}</button>
  );
}
export const Bar = ({ pct, cls = "bg-teal-600" }: { pct: number; cls?: string }) => (
  <div className="h-1.5 w-full rounded bg-slate-100 dark:bg-slate-800"><div className={`h-1.5 rounded ${cls}`} style={{ width: `${Math.min(100, pct)}%` }} /></div>
);

export function Modal({ title, children, onClose }: { title: string; children: ReactNode; onClose: () => void }) {
  useEffect(() => { const k = (e: KeyboardEvent) => e.key === "Escape" && onClose(); addEventListener("keydown", k); return () => removeEventListener("keydown", k); });
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/50 p-4" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div role="dialog" aria-modal="true" aria-label={title} className="card w-full max-w-md shadow-xl"><h2 className="mb-3 text-lg font-semibold">{title}</h2>{children}</div>
    </div>
  );
}

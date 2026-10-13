import { useEffect, useRef, useState } from "react";

export const TC: Record<string, string> = { credit_card: "#ef4444", aws_access_key: "#f97316", aadhaar: "#8b5cf6", pan: "#3b82f6", email: "#14b8a6", phone: "#eab308" };

export function useCountUp(n: number, ms = 800) {
  const [v, setV] = useState(0);
  useEffect(() => {
    let raf = 0; const t0 = performance.now();
    const step = (t: number) => { const p = Math.min(1, (t - t0) / ms); setV(Math.round(n * (1 - Math.pow(1 - p, 3)))); if (p < 1) raf = requestAnimationFrame(step); };
    raf = requestAnimationFrame(step); return () => cancelAnimationFrame(raf);
  }, [n]);
  return v;
}

type Slice = { key: string; label: string; value: number; color: string; detail?: string[] };
export function Donut({ data, onPick, centerLabel = "total" }: { data: Slice[]; onPick?: (k: string) => void; centerLabel?: string }) {
  const [hv, setHv] = useState<string | null>(null), [pos, setPos] = useState({ x: 0, y: 0 });
  const box = useRef<HTMLDivElement>(null);
  const R = 70, C = 2 * Math.PI * R, total = data.reduce((n, d) => n + d.value, 0);
  const live = data.filter((d) => d.value > 0), gap = live.length > 1 ? 2 : 0, h = data.find((d) => d.key === hv);
  let cum = 0;
  const move = (e: any) => { const r = box.current!.getBoundingClientRect(); setPos({ x: e.clientX - r.left, y: e.clientY - r.top }); };
  const W = box.current?.offsetWidth || 600;
  return (
    <div ref={box} className="relative flex flex-wrap items-center gap-6" onMouseMove={move} onMouseLeave={() => setHv(null)}>
      <svg viewBox="0 0 200 200" className="h-52 w-52 shrink-0" role="img" aria-label="Distribution chart">
        <circle cx="100" cy="100" r={R} fill="none" strokeWidth="24" className="stroke-slate-100 dark:stroke-slate-800" />
        {live.map((d) => {
          const len = (d.value / total) * C, off = cum; cum += len;
          return <circle key={d.key} data-slice={d.key} cx="100" cy="100" r={R} fill="none" stroke={d.color} strokeWidth={hv === d.key ? 32 : 24}
            strokeDasharray={`${Math.max(len - gap, 0)} ${C}`} strokeDashoffset={-off} transform="rotate(-90 100 100)"
            style={{ transition: "stroke-width .15s, opacity .15s", opacity: hv && hv !== d.key ? 0.4 : 1, cursor: onPick ? "pointer" : "default" }}
            onMouseEnter={() => setHv(d.key)} onClick={() => onPick?.(d.key)} />;
        })}
        <text x="100" y="98" textAnchor="middle" fontSize="26" fontWeight="600" className="fill-slate-900 dark:fill-slate-100">{(h ? h.value : total).toLocaleString()}</text>
        <text x="100" y="116" textAnchor="middle" fontSize="10" className="fill-slate-500">{h ? h.label : centerLabel}</text>
      </svg>
      <ul className="min-w-40 flex-1 space-y-1">
        {data.map((d) => (
          <li key={d.key}>
            <button className={`flex w-full items-center gap-2 rounded px-2 py-1 text-sm ${hv === d.key ? "bg-slate-100 dark:bg-slate-800" : ""}`} onMouseEnter={() => setHv(d.key)} onClick={() => onPick?.(d.key)}>
              <span className="h-3 w-3 rounded-sm" style={{ background: d.color }} /><span className="flex-1 text-left">{d.label}</span><b className="tabular-nums">{d.value.toLocaleString()}</b>
            </button>
          </li>
        ))}
      </ul>
      {h && (
        <div role="tooltip" className="pointer-events-none absolute z-10 w-56 rounded-[var(--r)] border border-slate-200 bg-white p-3 text-sm shadow-xl dark:border-slate-700 dark:bg-slate-900" style={{ left: pos.x > W - 250 ? pos.x - 234 : pos.x + 14, top: pos.y + 14 }}>
          <p className="flex items-center gap-2 font-semibold"><span className="h-2.5 w-2.5 rounded-full" style={{ background: h.color }} />{h.label}</p>
          <p className="mt-1">{h.value.toLocaleString()} <span className="text-slate-500">({total ? Math.round((h.value / total) * 100) : 0}%)</span></p>
          {h.detail?.map((x) => <p key={x} className="mt-0.5 text-xs text-slate-500">{x}</p>)}
          {onPick && <p className="mt-2 text-xs font-medium text-teal-700 dark:text-teal-400">Click to view</p>}
        </div>
      )}
    </div>
  );
}

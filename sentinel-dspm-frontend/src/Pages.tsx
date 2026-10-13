import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { RefreshCw } from "lucide-react";
import { TC, Donut, useCountUp } from "./charts";
import { api } from "./api";
import { Async, Badge, Bar, Empty, Err, Head, Modal, TYPES, Table, fmt, useLoad } from "./ui";

const SEVC: any = { critical: "bg-red-500", high: "bg-orange-500", medium: "bg-amber-500", low: "bg-sky-500", none: "bg-emerald-500" };

const RC: any = { critical: "#ef4444", high: "#f97316", medium: "#f59e0b", low: "#0ea5e9", none: "#10b981" };
const SO = ["critical", "high", "medium", "low"];
function Stat({ label, value, to }: any) {
  const n = useCountUp(value || 0), nav = useNavigate();
  return (
    <button onClick={() => nav(to)} className="card text-left transition hover:-translate-y-0.5 hover:border-teal-500">
      <p className="text-sm text-slate-500">{label}</p><p className="mt-1 text-3xl font-semibold tabular-nums">{n.toLocaleString()}</p>
    </button>
  );
}

export function Dashboard() {
  const nav = useNavigate();
  const s = useLoad("/api/v1/dashboard/summary"), f = useLoad("/api/v1/findings/", []), a = useLoad("/api/v1/alerts/", []), as = useLoad("/api/v1/assets/", []);
  const [open, setOpen] = useState<number | null>(null);
  const d = s.data || {}, risk = d.risk_summary || {};
  const am: any = useMemo(() => Object.fromEntries(as.data.map((x: any) => [x.id, x])), [as.data]);
  const types = useMemo(() => Object.keys(TYPES).map((k) => {
    const rows = f.data.filter((x: any) => x.data_type === k), top = [...rows].sort((x: any, y: any) => y.count - x.count)[0], worst = SO.find((sv) => rows.some((x: any) => x.severity === sv));
    return { key: k, label: TYPES[k], color: TC[k], value: rows.reduce((n: number, x: any) => n + x.count, 0),
      detail: [`${rows.length} file${rows.length === 1 ? "" : "s"} affected`, worst ? `Worst severity: ${worst}` : "", top ? `Most in ${am[top.asset_id]?.name || "asset #" + top.asset_id} (${top.count})` : ""].filter(Boolean) };
  }), [f.data, am]);
  const totalAssets = Math.max(1, d.total_assets || 0);
  const risks = ["critical", "high", "medium", "low", "none"].map((k) => {
    const names = as.data.filter((x: any) => x.risk_level === k).slice(0, 3).map((x: any) => x.name);
    return { key: k, label: k === "none" ? "No risk" : k[0].toUpperCase() + k.slice(1), color: RC[k], value: risk[k] ?? 0, detail: [`${Math.round(((risk[k] ?? 0) / totalAssets) * 100)}% of all assets`, ...(names.length ? [names.join(", ")] : [])] };
  });
  const top = [...as.data].filter((x: any) => x.risk_score > 0).sort((x: any, y: any) => y.risk_score - x.risk_score).slice(0, 6);
  const nOpen = a.data.filter((x: any) => x.status === "OPEN").length;
  return (
    <>
      <Head title="Dashboard" sub="Hover a chart to see details. Click a slice to open the matching findings.">
        <button className="btn2" onClick={() => [s, f, a, as].forEach((x) => x.reload())}><RefreshCw size={15} className={s.loading ? "animate-spin" : ""} />Refresh</button>
      </Head>
      <Async l={s}>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Stat label="Assets scanned" value={d.total_assets} to="/assets" /><Stat label="Active findings" value={d.total_findings} to="/findings" />
          <Stat label="Open alerts" value={nOpen} to="/alerts" /><Stat label="Data sources" value={d.total_datasources} to="/sources" />
        </div>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div className="card"><h2 className="mb-4 font-semibold">Sensitive records by type</h2><Donut data={types} centerLabel="records" onPick={(k) => nav(`/findings?type=${k}`)} /></div>
          <div className="card"><h2 className="mb-4 font-semibold">Assets by risk level</h2><Donut data={risks} centerLabel="assets" onPick={(k) => nav(`/assets?risk=${k}`)} /></div>
        </div>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div className="card">
            <h2 className="mb-3 font-semibold">Riskiest files</h2>
            {top.length === 0 ? <Empty t="No risky files yet. Run a scan to get started." /> : top.map((x: any) => (
              <div key={x.id} className="border-t border-slate-100 first:border-0 dark:border-slate-800">
                <button className="flex w-full items-center justify-between gap-3 py-2.5 text-left" aria-expanded={open === x.id} onClick={() => setOpen(open === x.id ? null : x.id)}>
                  <div className="min-w-0"><p className="truncate text-sm font-medium">{x.name}</p><p className="truncate text-xs text-slate-500">{x.path}</p></div><Badge v={x.risk_level} />
                </button>
                {open === x.id && (
                  <div className="flex flex-wrap gap-2 pb-3">
                    {f.data.filter((y: any) => y.asset_id === x.id).map((y: any) => <span key={y.id} className="rounded-full border border-slate-200 px-2 py-0.5 text-xs dark:border-slate-700"><span className="mr-1 inline-block h-2 w-2 rounded-full" style={{ background: TC[y.data_type] }} />{TYPES[y.data_type] || y.data_type}: <b>{y.count}</b></span>)}
                  </div>
                )}
              </div>
            ))}
          </div>
          <div className="card">
            <h2 className="mb-3 font-semibold">Latest alerts</h2>
            {a.data.length === 0 ? <Empty t="No alerts. Add an alert rule to be notified." /> : a.data.slice(0, 6).map((x: any) => (
              <button key={x.id} onClick={() => nav("/alerts")} className="flex w-full items-center justify-between gap-3 border-t border-slate-100 py-2.5 text-left first:border-0 hover:opacity-75 dark:border-slate-800">
                <div className="min-w-0"><p className="truncate text-sm font-medium">{x.title}</p><p className="text-xs text-slate-500">{fmt(x.created_at)}</p></div><Badge v={x.status} />
              </button>
            ))}
          </div>
        </div>
      </Async>
    </>
  );
}

export function Assets() {
  const l = useLoad("/api/v1/assets/", []);
  const [q, setQ] = useState(""), [lvl, setLvl] = useState(new URLSearchParams(location.search).get("risk") || "");
  const rows = l.data.filter((x: any) => (!lvl || x.risk_level === lvl) && (x.path + x.name).toLowerCase().includes(q.toLowerCase()));
  return (
    <>
      <Head title="Assets" sub="Every S3 object discovered by your scans.">
        <input className="input w-56" placeholder="Search name or path" value={q} onChange={(e) => setQ(e.target.value)} />
        <select className="input w-36" value={lvl} onChange={(e) => setLvl(e.target.value)}><option value="">All risk</option>{["critical", "high", "medium", "low", "none"].map((k) => <option key={k}>{k}</option>)}</select>
      </Head>
      <Async l={l}>
        <Table head={["Name", "Location", "Size", "Risk", "Last scanned"]} empty={rows.length ? "" : "No assets found. Run a scan first."}>
          {rows.map((x: any) => (
            <tr key={x.id}><td className="td font-medium">{x.name}</td><td className="td max-w-xs truncate text-slate-500">{x.path}</td><td className="td">{x.size != null ? `${(x.size / 1024).toFixed(1)} KB` : "—"}</td>
              <td className="td"><Badge v={x.risk_level} /> <span className="ml-1 text-xs text-slate-500">{x.risk_score}</span></td><td className="td text-slate-500">{fmt(x.last_scanned_at)}</td></tr>
          ))}
        </Table>
      </Async>
    </>
  );
}

export function Findings() {
  const l = useLoad("/api/v1/findings/", []), as = useLoad("/api/v1/assets/", []);
  const [t, setT] = useState(new URLSearchParams(location.search).get("type") || ""), [sev, setSev] = useState("");
  const am: any = Object.fromEntries(as.data.map((x: any) => [x.id, x]));
  const rows = l.data.filter((x: any) => (!t || x.data_type === t) && (!sev || x.severity === sev));
  return (
    <>
      <Head title="Findings" sub="Where sensitive data was detected, and how much.">
        <select className="input w-44" value={t} onChange={(e) => setT(e.target.value)}><option value="">All data types</option>{Object.entries(TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select>
        <select className="input w-36" value={sev} onChange={(e) => setSev(e.target.value)}><option value="">All severity</option>{["critical", "high", "medium", "low"].map((k) => <option key={k}>{k}</option>)}</select>
      </Head>
      <Async l={l}>
        <Table head={["File", "Data type", "Count", "Severity", "Last seen"]} empty={rows.length ? "" : "No findings match. Clean data is good news."}>
          {rows.map((x: any) => (
            <tr key={x.id}><td className="td"><p className="font-medium">{am[x.asset_id]?.name || `Asset #${x.asset_id}`}</p><p className="max-w-sm truncate text-xs text-slate-500">{am[x.asset_id]?.path}</p></td>
              <td className="td">{TYPES[x.data_type] || x.data_type}</td><td className="td font-semibold">{x.count}</td><td className="td"><Badge v={x.severity} /></td><td className="td text-slate-500">{fmt(x.last_seen_at)}</td></tr>
          ))}
        </Table>
      </Async>
    </>
  );
}

export function Alerts() {
  const l = useLoad("/api/v1/alerts/", []), as = useLoad("/api/v1/assets/", []);
  const [f, setF] = useState("OPEN"), [err, setErr] = useState(""), [rz, setRz] = useState<any>(null), [sure, setSure] = useState(false);
  const am: any = Object.fromEntries(as.data.map((x: any) => [x.id, x]));
  const set = async (id: number, status: string) => {
    setErr(""); try { await api(`/api/v1/alerts/${id}/status?status=${status}`, { method: "PATCH" }); l.reload(); } catch (e: any) { setErr(e.message); }
  };
  const rows = l.data.filter((x: any) => !f || x.status === f);
  return (
    <>
      <Head title="Alerts" sub="Raised when a file crosses one of your alert rule thresholds.">
        <select className="input w-40" value={f} onChange={(e) => setF(e.target.value)}><option value="">All</option>{["OPEN", "ACKNOWLEDGED", "RESOLVED"].map((k) => <option key={k}>{k}</option>)}</select>
      </Head>
      <Err m={err} />
      <Async l={l}>
        <Table head={["Alert", "File", "Found / limit", "Severity", "Status", ""]} empty={rows.length ? "" : "No alerts in this view."}>
          {rows.map((x: any) => (
            <tr key={x.id}><td className="td"><p className="font-medium">{x.title}</p><p className="text-xs text-slate-500">{fmt(x.created_at)}</p></td>
              <td className="td max-w-[14rem] truncate text-slate-500">{am[x.asset_id]?.path || `Asset #${x.asset_id}`}</td>
              <td className="td">{x.current_count} / {x.threshold}</td><td className="td"><Badge v={x.severity} /></td><td className="td"><Badge v={x.status} /></td>
              <td className="td"><div className="flex gap-2">
                {x.status === "OPEN" && <button className="btn2" onClick={() => set(x.id, "ACKNOWLEDGED")}>Acknowledge</button>}
                {x.status !== "RESOLVED" && <button className="btn2" onClick={() => { setSure(false); setRz(x); }}>Resolve</button>}
                {x.status === "RESOLVED" && <button className="btn2" onClick={() => set(x.id, "OPEN")}>Reopen</button>}
              </div></td></tr>
          ))}
        </Table>
      </Async>
      {rz && (
        <Modal title="Before you resolve this alert" onClose={() => setRz(null)}>
          <div className="rounded-[var(--rs)] bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-500/10 dark:text-amber-200">
            <b>Resolving does not delete anything.</b> It only marks the alert as handled. Make sure the sensitive data behind it (the findings) has been removed from the source first.
          </div>
          <p className="mt-4 text-sm font-medium">{rz.title}</p>
          <p className="break-all text-xs text-slate-500">{am[rz.asset_id]?.path || `Asset #${rz.asset_id}`} · {rz.current_count} {TYPES[rz.data_type] || rz.data_type || "sensitive"} record{rz.current_count === 1 ? "" : "s"} found</p>
          <label className="mt-4 flex items-start gap-2 text-sm"><input type="checkbox" className="mt-1 accent-teal-600" checked={sure} onChange={(e) => setSure(e.target.checked)} />I have removed this data from the file, or moved it somewhere secure.</label>
          <p className="mt-2 text-xs text-slate-500">Tip: run a new scan afterwards to confirm it is gone.</p>
          <div className="mt-4 flex justify-end gap-2"><button className="btn2" onClick={() => setRz(null)}>Cancel</button><button className="btn" disabled={!sure} onClick={() => { set(rz.id, "RESOLVED"); setRz(null); }}>Resolve alert</button></div>
        </Modal>
      )}
    </>
  );
}

export function Rules() {
  const l = useLoad("/api/v1/alert-rules/", []);
  const [name, setN] = useState(""), [dt, setDt] = useState("credit_card"), [th, setTh] = useState(1), [err, setErr] = useState("");
  const run = async (fn: () => Promise<any>) => { setErr(""); try { await fn(); l.reload(); } catch (e: any) { setErr(e.message); } };
  return (
    <>
      <Head title="Alert rules" sub="Alert when a single file contains at least this many records of a data type." />
      <form className="card mb-4 flex flex-wrap items-end gap-3" onSubmit={(e) => { e.preventDefault(); run(async () => { await api("/api/v1/alert-rules/", { method: "POST", body: { name, data_type: dt, threshold: th } }); setN(""); }); }}>
        <div className="min-w-48 flex-1"><label className="mb-1 block text-sm font-medium">Rule name</label><input className="input" required value={name} onChange={(e) => setN(e.target.value)} placeholder="Any credit card in a file" /></div>
        <div><label className="mb-1 block text-sm font-medium">Data type</label><select className="input" value={dt} onChange={(e) => setDt(e.target.value)}>{Object.entries(TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></div>
        <div><label className="mb-1 block text-sm font-medium">Threshold</label><input className="input w-24" type="number" min={1} value={th} onChange={(e) => setTh(+e.target.value)} /></div>
        <button className="btn">Add rule</button>
      </form>
      <Err m={err} />
      <Async l={l}>
        <Table head={["Rule", "Data type", "Threshold", "Active", ""]} empty={l.data.length ? "" : "No rules yet. Add one above."}>
          {l.data.map((x: any) => (
            <tr key={x.id}><td className="td font-medium">{x.name}</td><td className="td">{TYPES[x.data_type] || x.data_type}</td><td className="td">{x.threshold}</td>
              <td className="td"><button className="btn2" onClick={() => run(() => api(`/api/v1/alert-rules/${x.id}`, { method: "PUT", body: { is_active: !x.is_active } }))}>{x.is_active ? "Enabled" : "Disabled"}</button></td>
              <td className="td"><button className="btn2" onClick={() => confirm("Delete this rule?") && run(() => api(`/api/v1/alert-rules/${x.id}`, { method: "DELETE" }))}>Delete</button></td></tr>
          ))}
        </Table>
      </Async>
    </>
  );
}

export function Policies() {
  const l = useLoad("/api/v1/policies/", []), [err, setErr] = useState("");
  const toggle = async (p: any) => { setErr(""); try { await api(`/api/v1/policies/${p.id}/status`, { method: "PATCH", body: { is_active: !p.is_active } }); l.reload(); } catch (e: any) { setErr(e.message); } };
  return (
    <>
      <Head title="Policies" sub="Choose which data types the scanner reports as findings." />
      <Err m={err} />
      <Async l={l}>
        <div className="grid gap-4 md:grid-cols-2">
          {l.data.map((p: any) => (
            <div key={p.id} className="card flex items-start justify-between gap-4">
              <div><p className="font-medium">{p.name}</p><p className="mt-1 text-sm text-slate-500">{p.description || `Detects ${TYPES[p.data_type] || p.data_type} in scanned files.`}</p><div className="mt-2"><Badge v={p.severity} /></div></div>
              <button role="switch" aria-checked={p.is_active} aria-label={`Toggle ${p.name}`} onClick={() => toggle(p)} className={`relative h-6 w-11 shrink-0 rounded-full transition ${p.is_active ? "bg-teal-600" : "bg-slate-300 dark:bg-slate-700"}`}>
                <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-all ${p.is_active ? "left-[22px]" : "left-0.5"}`} />
              </button>
            </div>
          ))}
        </div>
      </Async>
    </>
  );
}

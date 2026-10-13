import { useState } from "react";
import { Archive, CheckCircle2, Database, Download, HardDrive, Play, Server, Table2 } from "lucide-react";
import { api, BASE, tok } from "./api";
import { useMe } from "./App";
import { Async, Badge, Err, Head, Modal, Spinner, Table, fmt, useLoad } from "./ui";

const STEPS = ["Account details", "Deploy role in AWS", "Verify access", "Create data source"];

function Connect({ done }: { done: () => void }) {
  const { user } = useMe();
  const [step, setStep] = useState(0), [acc, setAcc] = useState<any>(null), [tpl, setTpl] = useState(""), [err, setErr] = useState(""), [busy, setB] = useState(false);
  const [f, setF] = useState({ name: "", account_id: "", account_name: "", role_name: "SentinelDSPMRole", region: "ap-south-1" });
  const go = async (fn: () => Promise<void>) => { setB(true); setErr(""); try { await fn(); } catch (e: any) { setErr(e.message); } finally { setB(false); } };
  const create = () => go(async () => {
    const a = await api("/api/v1/cloud-accounts/aws/", { method: "POST", body: f }); setAcc(a);
    setTpl((await api(`/api/v1/cloud-accounts/aws/${a.id}/cloudformation-template`)).template); setStep(1);
  });
  const download = async () => {
    const r = await fetch(`${BASE}/api/v1/cloud-accounts/aws/${acc.id}/cloudformation-template/download`, { headers: { Authorization: `Bearer ${tok.get()}` } });
    const u = URL.createObjectURL(await r.blob()); const a = document.createElement("a"); a.href = u; a.download = `sentineldspm-aws-${acc.id}.yaml`; a.click(); URL.revokeObjectURL(u);
  };
  const verify = () => go(async () => { setAcc(await api(`/api/v1/cloud-accounts/aws/${acc.id}/verify`, { method: "POST" })); setStep(3); });
  const finish = () => go(async () => {
    await api("/api/v1/datasources/", { method: "POST", body: { name: f.name, type: "AWS", tenant_id: user.tenant_id, aws_cloud_account_id: acc.id, status: "active" } }); done();
  });
  const set = (k: string) => (e: any) => setF({ ...f, [k]: e.target.value });
  return (
    <div className="card mb-6">
      <ol className="mb-6 flex flex-wrap gap-x-6 gap-y-2 text-sm">
        {STEPS.map((s, i) => <li key={s} className={`flex items-center gap-2 ${i === step ? "font-semibold text-teal-700 dark:text-teal-400" : i < step ? "text-slate-500" : "text-slate-400"}`}>{i < step ? <CheckCircle2 size={16} className="text-teal-600" /> : <span className="grid h-5 w-5 place-items-center rounded-full border text-xs">{i + 1}</span>}{s}</li>)}
      </ol>
      {user.tenant_id === null && <Err m="System admins have no tenant. Sign in as a tenant admin to connect AWS." />}
      {step === 0 && (
        <form className="grid gap-4 md:grid-cols-2" onSubmit={(e) => { e.preventDefault(); create(); }}>
          <div><label className="mb-1 block text-sm font-medium">Connection name</label><input className="input" required value={f.name} onChange={set("name")} placeholder="Production AWS" /></div>
          <div><label className="mb-1 block text-sm font-medium">AWS account ID</label><input className="input" required pattern="\d{12}" title="12 digits" value={f.account_id} onChange={set("account_id")} placeholder="123456789012" /></div>
          <div><label className="mb-1 block text-sm font-medium">Account nickname</label><input className="input" required value={f.account_name} onChange={set("account_name")} /></div>
          <div><label className="mb-1 block text-sm font-medium">Region</label><input className="input" required pattern="[a-z]{2}-[a-z]+-\d+" value={f.region} onChange={set("region")} /></div>
          <div><label className="mb-1 block text-sm font-medium">IAM role name</label><input className="input" required value={f.role_name} onChange={set("role_name")} /></div>
          <div className="flex items-end"><button className="btn" disabled={busy || user.tenant_id === null}>{busy && <Spinner />}Continue</button></div>
        </form>
      )}
      {step === 1 && (
        <div>
          <p className="mb-3 text-sm text-slate-500">Deploy this CloudFormation template in the AWS account. It creates a role with read-only S3 access that only Sentinel can assume, protected by a unique external ID.</p>
          <pre className="max-h-64 overflow-auto rounded-md bg-slate-100 p-3 text-xs dark:bg-slate-950">{tpl}</pre>
          <div className="mt-4 flex gap-2"><button className="btn2" onClick={download}><Download size={16} />Download template</button><button className="btn" onClick={() => setStep(2)}>I deployed the stack</button></div>
        </div>
      )}
      {step === 2 && (
        <div><p className="mb-3 text-sm text-slate-500">We will try to assume the role in account {acc.account_id}.</p><Err m={err} />
          <div className="mt-3 flex gap-2"><button className="btn" onClick={verify} disabled={busy}>{busy && <Spinner />}Verify connection</button><button className="btn2" onClick={() => setStep(1)}>Back</button></div></div>
      )}
      {step === 3 && (
        <div><p className="mb-3 flex items-center gap-2 text-sm"><CheckCircle2 size={16} className="text-emerald-600" />Connection verified. Create the data source to start scanning.</p><Err m={err} />
          <button className="btn mt-3" onClick={finish} disabled={busy}>{busy && <Spinner />}Create data source</button></div>
      )}
      {step !== 2 && step !== 3 && <Err m={err} />}
    </div>
  );
}

const SERVICES: [string, string, any, boolean][] = [
  ["Amazon S3", "Buckets and files", Archive, true], ["Amazon EC2", "Virtual servers", Server, false],
  ["Amazon RDS", "Managed databases", Database, false], ["Amazon DynamoDB", "NoSQL tables", Table2, false], ["Amazon EBS", "Block storage volumes", HardDrive, false],
];
const DANGER = "btn bg-red-600! hover:bg-red-500!";

export function Sources() {
  const l = useLoad("/api/v1/datasources/", []);
  const [show, setShow] = useState(false), [dlg, setDlg] = useState<any>(null);
  const close = () => !dlg?.busy && setDlg(null);
  // Step 1: a data source with scans can't be deleted, so look for them before asking for confirmation.
  const check = async (x: any) => {
    setDlg({ ds: x });
    try { const all = await api("/api/v1/scans/"); setDlg({ ds: x, scans: all.filter((s: any) => s.datasource_id === x.id) }); }
    catch { setDlg({ ds: x, scans: [] }); }
  };
  const removeScans = async () => {
    setDlg({ ...dlg, busy: true, err: "" });
    const left: any[] = []; let err = "";
    for (const s of dlg.scans) { try { await api(`/api/v1/scans/${s.id}`, { method: "DELETE" }); } catch (e: any) { left.push(s); err = e.message; } }
    setDlg({ ds: dlg.ds, scans: left, err: left.length ? `Could not delete ${left.length} scan${left.length === 1 ? "" : "s"}: ${err}` : "" });
  };
  const remove = async () => {
    setDlg({ ...dlg, busy: true, err: "" });
    try { await api(`/api/v1/datasources/${dlg.ds.id}`, { method: "DELETE" }); setDlg(null); l.reload(); }
    catch (e: any) {
      const net = e.message.startsWith("Could not get a response");
      setDlg({ ds: dlg.ds, scans: dlg.scans, err: net ? `${e.message} This data source may still have scans or other data linked to it.` : e.message });
    }
  };
  const n = dlg?.scans?.length || 0;
  return (
    <>
      <Head title="Data sources" sub="Connect a cloud service for read-only scanning. Amazon S3 is available today; more services are on the way."><button className="btn" onClick={() => setShow(!show)}>{show ? "Close" : "Connect AWS account"}</button></Head>
      <div className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-5" aria-label="Supported services">
        {SERVICES.map(([name, desc, Icon, live]) => live ? (
          <button key={name} onClick={() => setShow(true)} className="card text-left transition hover:border-teal-500">
            <Icon size={22} className="text-teal-600" /><b className="mt-3 block text-sm">{name}</b><p className="text-xs text-slate-500">{desc}</p>
            <span className="mt-3 inline-block rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300">Available</span>
          </button>
        ) : (
          <div key={name} aria-disabled="true" title="Coming soon" className="card cursor-not-allowed select-none opacity-60 grayscale">
            <Icon size={22} className="text-slate-400" /><b className="mt-3 block text-sm">{name}</b><p className="text-xs text-slate-500">{desc}</p>
            <span className="mt-3 inline-block rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500 dark:bg-slate-800">Coming soon</span>
          </div>
        ))}
      </div>
      {show && <Connect done={() => { setShow(false); l.reload(); }} />}
      <Async l={l}>
        <Table head={["Name", "Type", "Status", "Created", ""]} empty={l.data.length ? "" : "No data sources. Connect an AWS account to begin."}>
          {l.data.map((x: any) => (
            <tr key={x.id}><td className="td font-medium">{x.name}</td><td className="td">{x.type}</td><td className="td"><Badge v={x.status} /></td><td className="td text-slate-500">{fmt(x.created_at)}</td>
              <td className="td"><button className="btn2" onClick={() => check(x)}>Delete</button></td></tr>
          ))}
        </Table>
      </Async>
      {dlg && (
        <Modal title={n ? "Delete its scans first" : "Delete data source?"} onClose={close}>
          {dlg.scans === undefined ? <div className="flex justify-center p-6"><Spinner /></div> : n > 0 ? (
            <>
              <p className="text-sm">“{dlg.ds.name}” has {n} scan{n === 1 ? "" : "s"}. A data source can only be deleted after all of its scans are deleted.</p>
              <ul className="my-3 max-h-40 divide-y divide-slate-100 overflow-auto rounded-[var(--rs)] border border-slate-200 text-sm dark:divide-slate-800 dark:border-slate-800">
                {dlg.scans.map((s: any) => <li key={s.id} className="flex items-center justify-between gap-2 px-3 py-2"><span className="truncate">{s.name}</span><Badge v={s.status} /></li>)}
              </ul>
              <p className="text-xs text-slate-500">Deleting a scan removes its history and the alerts it raised.</p>
              <div className="mt-3"><Err m={dlg.err} /></div>
              <div className="mt-4 flex justify-end gap-2"><button className="btn2" onClick={close}>Cancel</button><button className={DANGER} onClick={removeScans} disabled={dlg.busy}>{dlg.busy && <Spinner />}Delete {n} scan{n === 1 ? "" : "s"}</button></div>
            </>
          ) : (
            <>
              <p className="text-sm">This permanently deletes “{dlg.ds.name}”. Its scanned files and findings will no longer be tracked.</p>
              <div className="mt-3"><Err m={dlg.err} /></div>
              <div className="mt-4 flex justify-end gap-2"><button className="btn2" onClick={close}>Cancel</button><button className={DANGER} onClick={remove} disabled={dlg.busy}>{dlg.busy && <Spinner />}Delete data source</button></div>
            </>
          )}
        </Modal>
      )}
    </>
  );
}

export function Scans() {
  const ds = useLoad("/api/v1/datasources/", []), l = useLoad("/api/v1/scans/", []);
  const [del, setDel] = useState<any>(null), [delBusy, setDelBusy] = useState(false), [delErr, setDelErr] = useState("");
  const [dsId, setDs] = useState(""), [name, setN] = useState(""), [busy, setB] = useState(false), [err, setErr] = useState(""), [res, setRes] = useState<any>(null);
  const run = async (e: any) => {
    e.preventDefault(); setB(true); setErr(""); setRes(null);
    try { setRes(await api("/api/v1/scans/", { method: "POST", body: { name: name || `Scan ${new Date().toLocaleString()}`, datasource_id: +dsId } })); l.reload(); }
    catch (x: any) { setErr(x.message); l.reload(); } finally { setB(false); }
  };
  const doDel = async () => {
    setDelBusy(true); setDelErr("");
    try { await api(`/api/v1/scans/${del.id}`, { method: "DELETE" }); setDel(null); l.reload(); } catch (e: any) { setDelErr(e.message); } finally { setDelBusy(false); }
  };
  const dm: any = Object.fromEntries(ds.data.map((x: any) => [x.id, x]));
  const S = res?.summary;
  return (
    <>
      <Head title="Scans" sub="Read every supported file (txt, csv, json, pdf, docx, xlsx) in your S3 buckets." />
      <form onSubmit={run} className="card mb-4 flex flex-wrap items-end gap-3">
        <div className="min-w-48"><label className="mb-1 block text-sm font-medium">Data source</label>
          <select className="input" required value={dsId} onChange={(e) => setDs(e.target.value)}><option value="">Select…</option>{ds.data.map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}</select></div>
        <div className="min-w-48 flex-1"><label className="mb-1 block text-sm font-medium">Scan name (optional)</label><input className="input" value={name} onChange={(e) => setN(e.target.value)} /></div>
        <button className="btn" disabled={busy}>{busy ? <Spinner /> : <Play size={16} />}{busy ? "Scanning…" : "Start scan"}</button>
        {busy && <p className="w-full text-sm text-slate-500">Scanning runs to completion before it responds. Large accounts can take several minutes. Keep this tab open.</p>}
      </form>
      <Err m={err} />
      {S && (
        <div className="card mb-4"><h2 className="mb-3 font-semibold">Latest result: {res.name}</h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[["Files scanned", S.total_assets], ["Files with findings", S.assets_with_findings], ["Records detected", S.total_detections], ["Alerts raised", S.alerts_created], ["Increased", S.increased_findings], ["Decreased", S.decreased_findings], ["Resolved", S.resolved_findings], ["Unchanged", S.unchanged_findings]].map(([k, v]) => <div key={k as string}><p className="text-sm text-slate-500">{k}</p><p className="text-2xl font-semibold">{v}</p></div>)}
          </div></div>
      )}
      <Async l={l}>
        <Table head={["Scan", "Data source", "Status", "Started", "Completed", ""]} empty={l.data.length ? "" : "No scans yet."}>
          {[...l.data].reverse().map((x: any) => (
            <tr key={x.id}><td className="td font-medium">{x.name}</td><td className="td">{dm[x.datasource_id]?.name || `Data source #${x.datasource_id}`}{dm[x.datasource_id]?.type && <span className="ml-1.5 text-xs text-slate-500">{dm[x.datasource_id].type}</span>}</td><td className="td"><Badge v={x.status} /></td><td className="td text-slate-500">{fmt(x.started_at)}</td><td className="td text-slate-500">{fmt(x.completed_at)}</td><td className="td"><button className="btn2" disabled={["pending", "running"].includes(x.status)} onClick={() => { setDelErr(""); setDel(x); }}>Delete</button></td></tr>
          ))}
        </Table>
      </Async>
      {del && (
        <Modal title="Delete scan?" onClose={() => !delBusy && setDel(null)}>
          <p className="text-sm">This removes “{del.name}” from your scan history, along with the alerts it raised.</p>
          <div className="mt-3"><Err m={delErr} /></div>
          <div className="mt-4 flex justify-end gap-2"><button className="btn2" onClick={() => setDel(null)}>Cancel</button><button className={DANGER} onClick={doDel} disabled={delBusy}>{delBusy && <Spinner />}Delete scan</button></div>
        </Modal>
      )}
    </>
  );
}

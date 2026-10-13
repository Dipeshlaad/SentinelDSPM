import { useState } from "react";
import { useMe } from "./App";
import { api } from "./api";
import { Async, Badge, Err, Head, Table, fmt, useLoad } from "./ui";

export function Tenants() {
  const l = useLoad("/api/v1/tenants/", []);
  const [f, setF] = useState({ name: "", admin_email: "", admin_password: "" }), [err, setErr] = useState("");
  const set = (k: string) => (e: any) => setF({ ...f, [k]: e.target.value });
  return (
    <>
      <Head title="Tenants" sub="Customer organizations. Each gets its own admin." />
      <form className="card mb-4 grid gap-3 md:grid-cols-4" onSubmit={async (e) => { e.preventDefault(); setErr(""); try { await api("/api/v1/tenants/", { method: "POST", body: f }); setF({ name: "", admin_email: "", admin_password: "" }); l.reload(); } catch (x: any) { setErr(x.message); } }}>
        <input className="input" required placeholder="Organization name" value={f.name} onChange={set("name")} />
        <input className="input" type="email" required placeholder="Admin email" value={f.admin_email} onChange={set("admin_email")} />
        <input className="input" type="password" required placeholder="Admin password" value={f.admin_password} onChange={set("admin_password")} />
        <button className="btn">Create tenant</button>
      </form>
      <Err m={err} />
      <Async l={l}>
        <Table head={["ID", "Name", "Created"]} empty={l.data.length ? "" : "No tenants yet."}>
          {l.data.map((t: any) => <tr key={t.id}><td className="td">{t.id}</td><td className="td font-medium">{t.name}</td><td className="td text-slate-500">{fmt(t.created_at)}</td></tr>)}
        </Table>
      </Async>
    </>
  );
}

const rl = (n: string) => String(n).replace(/_/g, " ").toLowerCase().replace(/^\w/, (c) => c.toUpperCase());

export function UsersPage() {
  const { user } = useMe(), admin = user.tenant_id === null;
  const l = useLoad("/users/", []), roles = useLoad("/api/v1/roles/", []), tenants = useLoad(admin ? "/api/v1/tenants/" : null, []);
  const [f, setF] = useState<any>({ email: "", password: "", tenant_id: "", role_id: "" }), [err, setErr] = useState(""), [tip, setTip] = useState(false), [busy, setBusy] = useState(false);
  const set = (k: string) => (e: any) => setF({ ...f, [k]: e.target.value });
  // Tenant admins can never assign (or even see) the global System Admin role.
  const opts = (roles.data as any[]).filter((r) => admin || r.name !== "SYSTEM_ADMIN");
  const rn = (id: number) => (roles.data as any[]).find((r) => r.id === id)?.name || "";
  const tn = (id: number) => (tenants.data as any[]).find((t) => t.id === id)?.name || `Tenant #${id}`;
  const global = rn(+f.role_id) === "SYSTEM_ADMIN";
  const submit = async (e: any) => {
    e.preventDefault(); setErr(""); setBusy(true);
    try {
      const tenant_id = global ? null : admin ? +f.tenant_id : user.tenant_id;
      await api("/users/", { method: "POST", body: { email: f.email, password: f.password, tenant_id, role_id: +f.role_id } });
      setF({ email: "", password: "", tenant_id: "", role_id: "" }); l.reload();
    } catch (x: any) { setErr(x.message); } finally { setBusy(false); }
  };
  return (
    <>
      <Head title="Users" sub={admin ? "Accounts across all tenants." : "People in your organization."} />
      <form className={`card mb-4 grid gap-3 ${admin ? "md:grid-cols-5" : "md:grid-cols-4"}`} onSubmit={submit}>
        <input className="input" type="email" required placeholder="Email" value={f.email} onChange={set("email")} />
        <input className="input" type="password" required placeholder="Password" value={f.password} onChange={set("password")} />
        <select className="input" required aria-label="Role" value={f.role_id} onChange={set("role_id")}><option value="">Role…</option>{opts.map((r: any) => <option key={r.id} value={r.id}>{rl(r.name)}</option>)}</select>
        {admin && (
          <div className="relative" style={{ position: "relative" }} onMouseEnter={() => global && setTip(true)} onMouseLeave={() => setTip(false)} title={global ? "System admin is a global admin with access to all tenants." : undefined}>
            <select className="input" aria-label="Tenant" required={!global} disabled={global} value={global ? "" : f.tenant_id} onChange={set("tenant_id")}>
              {global ? <option value="">All tenants</option> : <><option value="">Tenant…</option>{tenants.data.map((t: any) => <option key={t.id} value={t.id}>{t.name}</option>)}</>}
            </select>
            {global && <div data-lock="tenant" className="cursor-not-allowed" style={{ position: "absolute", inset: 0 }} />}
            {tip && <div role="tooltip" className="absolute left-0 top-full z-20 mt-2 w-64 rounded-[var(--rs)] border border-slate-200 bg-white p-3 text-xs shadow-xl dark:border-slate-700 dark:bg-slate-900"><b>Global administrator.</b> A system admin has access to all tenants, so no tenant is assigned.</div>}
          </div>
        )}
        <button className="btn" disabled={busy}>Add user</button>
      </form>
      {roles.err && <p role="alert" className="mb-2 text-sm text-red-600 dark:text-red-400">Could not load roles: {roles.err}</p>}
      <Err m={err} />
      <Async l={l}>
        <Table head={admin ? ["Email", "Tenant", "Role", "Status", ""] : ["Email", "Role", "Status", ""]} empty={l.data.length ? "" : "No users."}>
          {l.data.map((u: any) => {
            const me = u.id === user.user_id;
            return (
              <tr key={u.id}><td className="td font-medium">{u.email}{me && <span className="ml-2 rounded-full bg-teal-50 px-2 py-0.5 text-xs text-teal-800 dark:bg-teal-500/15 dark:text-teal-300">You</span>}</td>
                {admin && <td className="td">{u.tenant_id == null ? (rn(u.role_id) === "SYSTEM_ADMIN" ? "All tenants" : "No tenant") : tn(u.tenant_id)}</td>}
                <td className="td">{rn(u.role_id) ? rl(rn(u.role_id)) : `Role #${u.role_id}`}</td><td className="td"><Badge v={u.is_active ? "active" : "inactive"} /></td>
                <td className="td"><button className="btn2" disabled={me} title={me ? "You can't deactivate your own account" : undefined} onClick={async () => { try { await api(`/users/${u.id}/status`, { method: "PATCH", body: { is_active: !u.is_active } }); l.reload(); } catch (x: any) { setErr(x.message); } }}>{u.is_active ? "Deactivate" : "Activate"}</button></td></tr>
            );
          })}
        </Table>
      </Async>
    </>
  );
}

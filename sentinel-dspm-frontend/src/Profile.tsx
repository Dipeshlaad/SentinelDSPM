import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Check, Copy, LogOut } from "lucide-react";
import { api } from "./api";
import { useMe } from "./App";
import { Badge, Head, Spinner, fmt } from "./ui";

export const nameOf = (email: string) => { const n = (email || "?").split("@")[0]; return n.charAt(0).toUpperCase() + n.slice(1); };
const pretty = (s: any) => String(s).replace(/_/g, " ").toLowerCase().replace(/^\w/, (c) => c.toUpperCase());
const left = (exp: number) => { const m = Math.max(0, Math.round((exp * 1000 - Date.now()) / 60000)); return m >= 60 ? `${Math.floor(m / 60)} h ${m % 60} min left` : `${m} min left`; };

export function Profile() {
  const { user, logout } = useMe(), nav = useNavigate();
  const [d, setD] = useState<any>(null), [copied, setCopied] = useState(false);
  useEffect(() => {
    (async () => {
      // Each lookup is optional: if the role lacks permission for one, the page falls back to the ids in the token.
      const ok = async (p: string) => { try { return await api(p); } catch { return null; } };
      const tenantId = user.tenant_id;
      const [me, role, tenant] = await Promise.all([ok(`/users/${user.user_id}`), ok(`/api/v1/roles/${user.role_id}`), tenantId != null ? ok(`/api/v1/tenants/${tenantId}`) : null]);
      const perms = role ? await ok(`/api/v1/role-permissions/${role.name}`) : null;
      const [ds, as, al] = tenantId != null ? await Promise.all(["/api/v1/datasources/", "/api/v1/assets/", "/api/v1/alerts/"].map(ok)) : [null, null, null];
      setD({ me, role, tenant, perms: perms?.permissions || [], ds, as, al });
    })();
  }, []);
  const admin = user.tenant_id === null, roleName = d?.role ? pretty(d.role.name) : `Role #${user.role_id}`;
  const rows: [string, any][] = [
    ["User ID", <span className="inline-flex items-center gap-2">{user.user_id}<button className="btn2 !px-2 !py-0.5" aria-label="Copy user ID" onClick={() => { navigator.clipboard?.writeText(String(user.user_id)).then(() => { setCopied(true); setTimeout(() => setCopied(false), 1500); }).catch(() => {}); }}>{copied ? <Check size={13} /> : <Copy size={13} />}</button></span>],
    ["Email", user.email], ["Role", `${roleName} (ID ${user.role_id})`], ["Account type", admin ? "System administrator" : "Tenant user"],
    ["Organization", admin ? "All tenants (platform level)" : `${d?.tenant?.name || "—"} (Tenant ID ${user.tenant_id})`],
    ["Account status", d?.me ? <Badge v={d.me.is_active ? "active" : "inactive"} /> : "—"], ["Member since", fmt(d?.me?.created_at)],
    ["Session expires", `${fmt(new Date(user.exp * 1000).toISOString())} · ${left(user.exp)}`],
  ];
  const stats = [["Data sources", d?.ds?.length], ["Assets scanned", d?.as?.length], ["Open alerts", d?.al?.filter((x: any) => x.status === "OPEN").length]];
  return (
    <>
      <Head title="My profile" sub="Your account, role and access in Sentinel DSPM.">
        <button className="btn2" onClick={() => { logout(); nav("/login"); }}><LogOut size={15} />Sign out</button>
      </Head>
      {!d ? <div className="flex justify-center p-10"><Spinner /></div> : (
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="card flex flex-col items-center text-center lg:col-span-1">
            <span className="grid h-24 w-24 place-items-center rounded-full bg-teal-600 text-4xl font-semibold text-white">{nameOf(user.email)[0]}</span>
            <h2 className="mt-4 text-xl font-semibold">{nameOf(user.email)}</h2><p className="text-sm text-slate-500">{user.email}</p>
            <div className="mt-3 flex gap-2"><Badge v="active" /><span className="rounded-full bg-teal-50 px-2 py-0.5 text-xs font-medium text-teal-800 dark:bg-teal-500/15 dark:text-teal-300">{roleName}</span></div>
            {!admin && <div className="mt-6 grid w-full grid-cols-3 gap-2 border-t border-slate-100 pt-4 dark:border-slate-800">{stats.map(([k, v]) => <div key={k as string}><p className="text-xl font-semibold">{v ?? "—"}</p><p className="text-xs text-slate-500">{k}</p></div>)}</div>}
          </div>
          <div className="space-y-4 lg:col-span-2">
            <div className="card"><h2 className="mb-2 font-semibold">Account details</h2>
              <dl>{rows.map(([k, v]) => <div key={k} className="grid grid-cols-3 gap-3 border-t border-slate-100 py-2.5 text-sm first:border-0 dark:border-slate-800"><dt className="text-slate-500">{k}</dt><dd className="col-span-2 break-words font-medium">{v}</dd></div>)}</dl></div>
            <div className="card"><h2 className="mb-3 font-semibold">What you can do</h2>
              {d.perms.length ? <div className="flex flex-wrap gap-2">{d.perms.map((p: string) => <span key={p} className="rounded-full border border-slate-200 px-2.5 py-1 font-mono text-xs dark:border-slate-700">{p}</span>)}</div>
                : <p className="text-sm text-slate-500">Permission details are not available for your role.</p>}</div>
          </div>
        </div>
      )}
    </>
  );
}

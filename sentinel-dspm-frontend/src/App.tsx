import { createContext, useContext, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, NavLink, Outlet, useNavigate } from "react-router-dom";
import { Shield, LayoutDashboard, Cloud, Activity, Database, ShieldAlert, Bell, SlidersHorizontal, ScrollText, Building2, Users as UsersIcon, LogOut } from "lucide-react";
import { tok, jwt, api } from "./api";
import { ThemeToggle } from "./ui";
import { Login } from "./Auth";
import { Dashboard, Assets, Findings, Alerts, Rules, Policies } from "./Pages";
import { Sources, Scans } from "./Cloud";
import { Tenants, UsersPage } from "./Admin";
import { Profile, nameOf } from "./Profile";

export const Ctx = createContext<any>(null);
export const useMe = () => useContext(Ctx);

function Shell() {
  const { user, logout } = useMe(), nav = useNavigate();
  const admin = user.tenant_id === null;
  // null = still loading. Users is for admins only; if the role can't be looked up we show it and let the server decide.
  const [roleName, setRoleName] = useState<string | null>(null);
  useEffect(() => { api(`/api/v1/roles/${user.role_id}`).then((r) => setRoleName(r.name)).catch(() => setRoleName("")); }, [user.role_id]);
  const canUsers = admin || roleName === "TENANT_ADMIN" || roleName === "";
  const items = [
    ["/", "Dashboard", LayoutDashboard], ["/sources", "Data sources", Cloud], ["/scans", "Scans", Activity], ["/assets", "Assets", Database],
    ["/findings", "Findings", ShieldAlert], ["/alerts", "Alerts", Bell], ["/rules", "Alert rules", SlidersHorizontal], ["/policies", "Policies", ScrollText],
    ...(admin ? [["/tenants", "Tenants", Building2]] : []), ...(canUsers ? [["/users", "Users", UsersIcon]] : []),
  ] as any[];
  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-slate-200 bg-white p-4 md:flex dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-6 flex items-center gap-2 px-2 text-lg font-bold"><Shield className="text-teal-600" /> Sentinel DSPM</div>
        <nav className="flex flex-1 flex-col gap-0.5">
          {items.map(([to, label, Icon]) => (
            <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-50 text-teal-800 dark:bg-teal-500/10 dark:text-teal-300" : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"}`}>
              <Icon size={17} />{label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-slate-200 pt-3 dark:border-slate-800">
          <NavLink to="/profile" title="View your profile" className={({ isActive }) => `flex items-center gap-3 rounded-[var(--rs)] px-2 py-2 hover:bg-slate-100 dark:hover:bg-slate-800 ${isActive ? "bg-slate-100 dark:bg-slate-800" : ""}`}>
            <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-teal-600 text-sm font-semibold text-white">{nameOf(user.email)[0]}</span>
            <span className="min-w-0"><b className="block truncate text-sm">{nameOf(user.email)}</b><span className="block truncate text-xs text-slate-500">View profile</span></span>
          </NavLink>
          <div className="mt-3 flex gap-2"><ThemeToggle /><button className="btn2" aria-label="Sign out" onClick={() => { logout(); nav("/login"); }}><LogOut size={16} /></button></div>
        </div>
      </aside>
      <main className="min-w-0 flex-1">
        <div className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-2 md:hidden dark:border-slate-800 dark:bg-slate-900">
          <b className="flex items-center gap-2"><Shield size={18} className="text-teal-600" />Sentinel</b>
          <div className="flex gap-2"><ThemeToggle /><button className="btn2" aria-label="Sign out" onClick={() => { logout(); nav("/login"); }}><LogOut size={16} /></button></div>
        </div>
        <div className="mx-auto max-w-6xl p-4 md:p-8"><Outlet /></div>
      </main>
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(tok.get());
  const user = jwt(token);
  const valid = user && user.exp * 1000 > Date.now();
  const login = (t: string, remember = false) => { tok.set(t, remember); setToken(t); };
  const logout = () => { tok.clear(); setToken(null); };
  return (
    <Ctx.Provider value={{ user, login, logout }}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={valid ? <Navigate to="/" /> : <Login />} />
          <Route element={valid ? <Shell /> : <Navigate to="/login" />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/sources" element={<Sources />} />
            <Route path="/scans" element={<Scans />} />
            <Route path="/assets" element={<Assets />} />
            <Route path="/findings" element={<Findings />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/policies" element={<Policies />} />
            <Route path="/tenants" element={user?.tenant_id === null ? <Tenants /> : <Navigate to="/" />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/profile" element={<Profile />} />
          </Route>
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </Ctx.Provider>
  );
}

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, Eye, EyeOff } from "lucide-react";
import { api } from "./api";
import { useMe } from "./App";
import { TC } from "./charts";
import { Err, Spinner, ThemeToggle } from "./ui";

const FEED: [string, string, string, number, string][] = [
  ["payroll_2026.csv", "PAN", "pan", 128, "ABCDE••••F"], ["customers_export.json", "Aadhaar", "aadhaar", 342, "•••• •••• 4821"],
  ["billing/cards.txt", "Credit card", "credit_card", 57, "4111 •••• •••• 1111"], ["deploy/.env.bak", "AWS access key", "aws_access_key", 3, "AKIA••••••••••••"],
  ["hr/contacts.xlsx", "Phone", "phone", 910, "+91 ••••• ••231"], ["invoices_q3.pdf", "Email", "email", 76, "a•••@corp.com"],
];

function LiveScan() {
  const [i, setI] = useState(0);
  useEffect(() => { const t = setInterval(() => setI((x) => x + 1), 1800); return () => clearInterval(t); }, []);
  let total = 0; for (let x = 0; x <= i; x++) total += FEED[x % FEED.length][3];
  const rows = [0, 1, 2, 3].map((k) => i - k).filter((x) => x >= 0).map((x) => ({ id: x, r: FEED[x % FEED.length] }));
  return (
    <div className="w-full max-w-md rounded-2xl border border-white/15 bg-white/10 p-5 backdrop-blur">
      <div className="mb-3 flex items-center justify-between text-sm">
        <span className="flex items-center gap-2"><span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />Scanning s3://acme-prod</span>
        <span className="tabular-nums text-white/70">{total.toLocaleString()} records</span>
      </div>
      <div key={i} className="mb-4 h-1 overflow-hidden rounded bg-white/15"><div className="fill h-1 bg-teal-400" /></div>
      <ul className="space-y-2">
        {rows.map(({ id, r }) => (
          <li key={id} className="slidein flex items-center gap-3 rounded-lg bg-black/20 px-3 py-2 text-sm">
            <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: TC[r[2]] }} />
            <div className="min-w-0 flex-1"><p className="truncate">{r[0]}</p><p className="truncate font-mono text-xs text-white/50">{r[4]}</p></div>
            <span className="text-right text-xs"><b className="block text-base">{r[3]}</b>{r[1]}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Frame({ title, sub, children }: any) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[1.1fr_1fr]">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-slate-900 p-12 text-white lg:flex">
        <div className="blob absolute -left-24 -top-24 h-96 w-96 rounded-full bg-teal-500/30 blur-3xl" />
        <div className="blob absolute -bottom-32 right-0 h-[28rem] w-[28rem] rounded-full bg-teal-400/20 blur-3xl" style={{ animationDelay: "-6s" }} />
        <div className="relative flex items-center gap-2 text-lg font-bold"><Shield className="text-teal-400" /> Sentinel DSPM</div>
        <div className="relative space-y-8">
          <div><p className="max-w-md text-4xl font-semibold leading-tight">Know exactly where your sensitive data sits in your cloud.</p>
            <p className="mt-3 max-w-md text-white/60">Read-only access. We find cards, PAN, Aadhaar and AWS keys, then alert you.</p></div>
          <LiveScan />
        </div>
        <p className="relative text-sm text-white/40">Detected values are never stored. Only counts and locations.</p>
      </div>
      <div className="relative flex items-center justify-center p-6">
        <div className="absolute right-4 top-4 flex items-center gap-3"><ThemeToggle /></div>
        <div className="w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2 text-lg font-bold lg:hidden"><Shield className="text-teal-600" /> Sentinel DSPM</div>
          <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
          <p className="mb-6 mt-1 text-sm text-slate-500">{sub}</p>
          {children}
        </div>
      </div>
    </div>
  );
}

export function Login() {
  const { login } = useMe(), nav = useNavigate();
  const [email, setE] = useState(localStorage.lastEmail || ""), [remember, setRem] = useState(!!localStorage.lastEmail), [password, setP] = useState(""), [show, setShow] = useState(false), [err, setErr] = useState(""), [busy, setB] = useState(false);
  const submit = async (e: any) => {
    e.preventDefault(); setB(true); setErr("");
    try { const r = await api("/api/v1/auth/login", { method: "POST", body: { email, password } }); if (remember) localStorage.lastEmail = email; else localStorage.removeItem("lastEmail"); login(r.access_token, remember); nav("/"); }
    catch (x: any) { setErr(x.message); } finally { setB(false); }
  };
  return (
    <Frame title="Sign in" sub="Welcome back. Enter your details to continue.">
      <form onSubmit={submit} className="space-y-4">
        <div><label className="mb-1 block text-sm font-medium">Email</label><input className="input" type="email" required autoFocus value={email} onChange={(e) => setE(e.target.value)} /></div>
        <div><label className="mb-1 block text-sm font-medium">Password</label>
          <div className="relative"><input className="input pr-10" type={show ? "text" : "password"} required value={password} onChange={(e) => setP(e.target.value)} />
            <button type="button" aria-label={show ? "Hide password" : "Show password"} onClick={() => setShow(!show)} className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200">{show ? <EyeOff size={17} /> : <Eye size={17} />}</button></div></div>
        <label className="flex cursor-pointer items-center gap-2 text-sm"><input type="checkbox" className="accent-teal-600" checked={remember} onChange={(e) => setRem(e.target.checked)} />Remember me<span className="text-xs text-slate-500">(stay signed in on this device)</span></label>
        <Err m={err} />
        <button className="btn w-full py-2.5" disabled={busy}>{busy && <Spinner />}Sign in</button>
      </form>
    </Frame>
  );
}

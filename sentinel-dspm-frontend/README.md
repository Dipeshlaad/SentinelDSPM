# Sentinel DSPM – Frontend

React + Vite + TypeScript + Tailwind v4. Light/dark toggle, a single Violet design, animated login, interactive pie-chart dashboard, JWT login, all backend routers wired.

```bash
cp .env.example .env      # VITE_API_URL -> your FastAPI URL
npm install
npm run dev               # http://localhost:5173 (already allowed by your CORS config)
```
Backend: `uvicorn app.main:app --reload --port 8000`

First run: open `/setup` to create the system admin, sign in, create a tenant (Tenants page), then sign in as that tenant's admin to connect AWS.

## Known limits (backend-side, for the next iteration)
- No endpoint to list AWS cloud accounts, so the connect wizard is single-session.
- `POST /scans/` blocks until the scan finishes (needs background job + polling).
- Findings/alerts return only `asset_id`; the UI joins against `/assets/` client-side.
- No audit-log, per-type summary, or "current user permissions" endpoints.

## Deleting data sources / scans
Apply the two small changes in `backend-patch/` (see its README) so the server answers with a clear message instead of a 500, and so scans can be deleted.

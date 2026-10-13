from fastapi import FastAPI

from app.models import tenant
from app.api import tenants
from app.api import users
from app.api import permissions
from app.api import roles
from app.api import role_permission
from app.api import auth
from app.api import datasources
from app.api import scans
from app.api import bootstrap
from app.api import assets
from app.api.findings import router as findings_router
from app.api.dashboard import router as dashboard_router
from app.api.alert_rules import router as alert_rules_router
from app.api.alerts import router as alerts_router
from app.api import policies
from app.api import aws_cloud_accounts
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Sentinel DSPM",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(
    tenants.router
)


app.include_router(
    users.router
)

app.include_router(

    permissions.router

)

app.include_router(
    roles.router
)

app.include_router(
    role_permission.router
)

app.include_router(
    auth.router
)

app.include_router(
    datasources.router
)

app.include_router(
    scans.router
)

app.include_router(
    bootstrap.router
)

app.include_router(
    assets.router
)

app.include_router(
    findings_router
)

app.include_router(
    dashboard_router
)

app.include_router(
    alert_rules_router
)

app.include_router(
    alerts_router
)

app.include_router(
    policies.router
)

app.include_router(
    aws_cloud_accounts.router
)
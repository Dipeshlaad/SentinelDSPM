from app.models.audit_log import AuditLog


def create_audit_log(
    db,
    user_id: int | None,
    tenant_id: int | None,
    action: str,
    resource_type: str,
    resource_id: int | None = None,
    details: str | None = None,
):
    audit_log = AuditLog(
        user_id=user_id,
        tenant_id=tenant_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
    )

    db.add(audit_log)

    return audit_log
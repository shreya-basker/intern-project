from app.models import AuditLog


async def create_audit_log(
    db,
    user_id: int,
    action: str,
    resource: str,
    resource_id: int,
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
    )

    db.add(log)

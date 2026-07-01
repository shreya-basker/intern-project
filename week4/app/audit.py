from week4.app.models import AuditLog


async def log_action(
    db,
    user_id: int,
    action: str,
    resource: str,
    resource_id: int | None = None,
) -> None:
    """Call after every state-changing operation."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
    )
    db.add(entry)
    await db.commit()

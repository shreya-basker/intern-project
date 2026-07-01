from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from week4.app.database import get_db
from week4.app.dependencies import require_permission
from week4.app.models import AuditLog

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.get("/audit-logs")
async def get_audit_logs(
    current_user=Depends(require_permission("audit", "read")),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50))

    return result.scalars().all()

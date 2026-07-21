from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ErrorLog
from app.schema import ErrorLogResponse, ErrorLogSummary

router = APIRouter(prefix="/error-logs", tags=["error logs"])


@router.get("/", response_model=list[ErrorLogSummary])
async def error_log_response(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ErrorLog).order_by(ErrorLog.timestamp.desc()))
    return result.scalars().all()


@router.get("/{error_id}", response_model=ErrorLogResponse)
async def get_error_log(error_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ErrorLog).where(ErrorLog.id == error_id))
    error = result.scalar_one_or_none()
    if error is None:
        raise HTTPException(status=404, detail="error not found")
    return error

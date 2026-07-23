import logging
from datetime import datetime

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.error_analysis.fingerprint import generate_fingerprint
from app.models import ErrorGroup, ErrorLog

logger = logging.getLogger(__name__)


async def log_error(
    session: AsyncSession,
    request: Request,
    exception: Exception,
    stack_trace: str,
    user_id: int | None = None,
) -> ErrorLog:
    try:
        fingerprint = generate_fingerprint(
            exception_type=type(exception).__name__,
            endpoint=request.url.path,
            message=str(exception),
        )
        result = await session.execute(
            select(ErrorGroup).where(ErrorGroup.fingerprint == fingerprint)
        )
        group = result.scalar_one_or_none()
        if group is None:
            group = ErrorGroup(fingerprint=fingerprint, occurrences=1)
            session.add(group)
            await session.flush()
        else:
            group.occurrences += 1
            group.last_seen = datetime.now()

        error = ErrorLog(
            endpoint=request.url.path,
            http_method=request.method,
            user_id=user_id,
            exception_type=type(exception).__name__,
            error_message=str(exception),
            stack_trace=stack_trace,
            analysis_time=None,
            root_cause=None,
            suggested_fix=None,
            llm_model=None,
            fingerprint=fingerprint,
            group_id=group.id,
        )
        session.add(error)
        await session.commit()
        await session.refresh(error)
        return error

    except Exception as log_exception:
        await session.rollback()
        logger.exception("Failed to log application error : %s", log_exception)
        raise

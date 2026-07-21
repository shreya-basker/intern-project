import logging

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ErrorLog

logger = logging.getLogger(__name__)


async def log_error(
    session: AsyncSession,
    request: Request,
    exception: Exception,
    stack_trace: str,
    user_id: int | None = None,
) -> None:
    try:
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
        )
        session.add(error)
        await session.commit()

    except Exception as log_exception:
        await session.rollback()
        logger.exception("Failed to log application error : %s", log_exception)

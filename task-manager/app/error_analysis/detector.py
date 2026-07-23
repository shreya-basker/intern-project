from datetime import datetime

from sqlalchemy import select

from app.ai.service import GeminiService
from app.database import AsyncSessionLocal
from app.models import ErrorLog

service = GeminiService()


async def process_errors(error_id: int) -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ErrorLog).where(ErrorLog.id == error_id))

        error = result.scalar_one_or_none()

        if error is None:
            print(f"Error with ID {error_id} not found.")
            return

        try:
            error.status = "processing"
            await session.commit()

            analysis = service.analyze(error)

            error.summary = analysis.summary
            error.root_cause = analysis.root_cause
            error.suggested_fix = analysis.suggested_fix
            error.severity = analysis.severity
            error.confidence = analysis.confidence
            error.analysis_time = datetime.now()
            error.status = "completed"
            error.llm_model = service.MODEL

            await session.commit()

        except Exception:
            await session.rollback()

            error.status = "pending"
            await session.commit()

            raise

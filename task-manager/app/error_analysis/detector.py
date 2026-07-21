import asyncio
from datetime import datetime

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.error_analysis.analyzer import analyze_error
from app.models import ErrorLog


async def detect_errors() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ErrorLog).where(ErrorLog.status == "pending"))

        pending_errors = result.scalars().all()

        for error in pending_errors:
            try:
                analysis = await analyze_error(error)

                error.root_cause = analysis["root_cause"]
                error.suggested_fix = analysis["suggested_fix"]
                error.llm_model = analysis["llm_model"]
                error.analysis_time = datetime.now()
                error.status = "completed"

                await session.commit()

            except Exception as e:
                await session.rollback()
                if "429" in str(e):
                    print("Gemini quota exceeded. Remaining errors will be processed later")
                    break
                print(f"Failed to analyze error {error.id}: {e}")
                continue


if __name__ == "__main__":
    asyncio.run(detect_errors())

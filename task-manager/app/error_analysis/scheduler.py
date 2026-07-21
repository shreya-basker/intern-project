from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.error_analysis.detector import detect_errors

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    scheduler.add_job(
        detect_errors,
        trigger="interval",
        # seconds = 20,
        minutes=30,
        id="error_detector",
        replace_existing=True,
    )

    scheduler.start()

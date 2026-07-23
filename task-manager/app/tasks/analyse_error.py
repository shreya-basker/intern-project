from asgiref.sync import async_to_sync

from app.core.celery import celery_app
from app.error_analysis.detector import process_errors


@celery_app.task(
    bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=3
)
def analyse_error_task(self, error_id: int):
    async_to_sync(process_errors)(error_id)

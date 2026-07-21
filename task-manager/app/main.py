import time
import traceback
from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.responses import Response

from app.database import AsyncSessionLocal
from app.error_analysis.logger import log_error
from app.error_analysis.scheduler import start_scheduler
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.comments import router as comment_router
from app.routers.error_logs import router as error_router
from app.routers.project import router as project_router
from app.routers.tasks import router as task_router
from app.routers.test_errors import router as test_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()

    yield
    from app.error_analysis.scheduler import scheduler

    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)
app.include_router(comment_router)
app.include_router(admin_router)
app.include_router(error_router)
app.include_router(test_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "week 3 api running"}


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()
    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        print(
            f"{request.method} {request.url.path} -> "
            f"{response.status_code} ({duration_ms:.1f}ms)"
        )
        return response
    except Exception as exc:
        stack_trace = traceback.format_exc()
        async with AsyncSessionLocal() as session:
            await log_error(
                session=session,
                request=request,
                exception=exc,
                stack_trace=stack_trace,
                user_id=None,  # We'll replace this with the authenticated user later
            )
        raise

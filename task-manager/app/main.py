import time
import traceback
from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.database import AsyncSessionLocal
from app.error_analysis.logger import log_error
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.comments import router as comment_router
from app.routers.error_logs import router as error_router
from app.routers.project import router as project_router
from app.routers.tasks import router as task_router
from app.routers.test_errors import router as test_router
from app.tasks.analyse_error import analyse_error_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)
app.include_router(comment_router)
app.include_router(admin_router)
app.include_router(error_router)
app.include_router(test_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    stack_trace = traceback.format_exc()
    async with AsyncSessionLocal() as session:
        error = await log_error(
            session=session,
            request=request,
            exception=exc,
            stack_trace=stack_trace,
            user_id=None,
        )
    analyse_error_task.delay(error.id)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "week 3 api running"}


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()

    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    print(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)")
    return response

import time
from collections.abc import Callable

from fastapi import FastAPI, Request
from starlette.responses import Response

from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.comments import router as comment_router
from app.routers.project import router as project_router
from app.routers.tasks import router as task_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)
app.include_router(comment_router)
app.include_router(admin_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "week 3 api running"}


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    print(
        f"{request.method} {request.url.path} -> " f"{response.status_code} ({duration_ms:.1f}ms)"
    )
    return response

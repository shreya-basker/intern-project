import time
from collections.abc import Callable

from fastapi import FastAPI, Request
from starlette.responses import Response

from app.routers.auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)


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

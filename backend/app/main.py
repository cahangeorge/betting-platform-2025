from contextlib import asynccontextmanager
import re
from typing import Any

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import v1_router
from app.config import get_settings

settings = get_settings()


class FlexibleCORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS that allows any *.trycloudflare.com + configured origins."""

    TUNNEL_PATTERN = re.compile(r"^https://[a-zA-Z0-9-]+\.trycloudflare\.com$")

    def __init__(self, app: Any, allowed_origins: list[str]):
        super().__init__(app)
        self.allowed_origins = set(allowed_origins)

    def _is_allowed(self, origin: str) -> bool:
        if "*" in self.allowed_origins:
            return True
        if origin in self.allowed_origins:
            return True
        if self.TUNNEL_PATTERN.match(origin):
            return True
        return False

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            origin = request.headers.get("origin", "")
            if self._is_allowed(origin):
                return Response(
                    status_code=204,
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT",
                        "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With",
                        "Access-Control-Max-Age": "600",
                    },
                )
            return Response(status_code=204)

        response = await call_next(request)
        origin = request.headers.get("origin", "")
        if origin and self._is_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.jwt_secret in ("dev-secret-change-in-production", "dev-jwt-secret-change-in-production"):
        import warnings
        warnings.warn("BET_JWT_SECRET is not set — using insecure dev fallback. Set BET_JWT_SECRET in production.")
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    FlexibleCORSMiddleware,
    allowed_origins=settings.cors_origin_list,
)

app.include_router(v1_router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}

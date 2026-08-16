from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    from app.database import engine

    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
    )

    # Middleware (order matters — last added = first executed)
    from app.middleware.security import SecurityHeadersMiddleware

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=[
        #     "http://localhost:3000",
        #     "http://127.0.0.1:3000",
        #     "http://localhost:5173",
        #     "http://127.0.0.1:5173",
        # ],
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="phoenix _session",
        max_age=60 * 60 * 24 * 7,  # 7 days
        https_only=settings.is_production,
    )

    # Rate limiter
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    from app.middleware.rate_limit import limiter

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Static files
    app.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "static")),
        name="static",
    )

    # Register routers
    _register_routers(app)

    # Mount SQLAdmin
    _mount_admin(app)

    # Serve React SPA after API routes are in place.
    _mount_react_frontend(app)

    return app


def _register_routers(app: FastAPI) -> None:
    from app.routers.api import payments as payments_api

    app.include_router(payments_api.router)

    from app.routers.api import router as api_router

    app.include_router(api_router)

    # Auth API routes (fastapi-users)
    from app.auth import bearer_backend, cookie_backend, fastapi_users
    from app.schemas.user import UserCreate, UserRead, UserUpdate

    app.include_router(
        fastapi_users.get_auth_router(cookie_backend),
        prefix="/api/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_auth_router(bearer_backend),
        prefix="/api/auth/bearer",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/api/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/api/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/api/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/api/users",
        tags=["users"],
    )


def _mount_admin(app: FastAPI) -> None:
    try:
        from app.admin import setup_admin

        setup_admin(app)
    except Exception:
        if settings.debug:
            import traceback

        traceback.print_exc()


def _mount_react_frontend(app: FastAPI) -> None:
    # In development, the Vite dev server on :3000 serves the frontend.
    # FastAPI only serves the SPA in production (when settings.debug is False).
    if not settings.debug and FRONTEND_DIST_DIR.exists():
        assets_dir = FRONTEND_DIST_DIR / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend-assets")

        index_file = FRONTEND_DIST_DIR / "index.html"

        @app.get("/", include_in_schema=False)
        async def spa_index():
            return FileResponse(index_file)

        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa_fallback(full_path: str):
            if full_path.startswith(("api/", "static/", "assets/", "admin/")):
                return HTMLResponse(status_code=404, content="Not Found")
            if full_path == "placeholder.svg":
                return FileResponse(BASE_DIR / "static" / "images" / "placeholder.svg")
            requested_file = FRONTEND_DIST_DIR / full_path
            if requested_file.is_file():
                return FileResponse(requested_file)
            return FileResponse(index_file)

        return

    @app.get("/", include_in_schema=False)
    async def frontend_dev_info():
        return HTMLResponse(
            status_code=200,
            content=(
                "Phoenix  API is running. "
            ),
        )


app = create_app()

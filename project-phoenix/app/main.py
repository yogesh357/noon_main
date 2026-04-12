from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent


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
    from app.middleware.i18n import I18nMiddleware
    from app.middleware.security import SecurityHeadersMiddleware

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(I18nMiddleware)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="phoenix_session",
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

    return app


def _register_routers(app: FastAPI) -> None:
    # Page routes (server-rendered HTML)
    from app.routers.pages import home as home_pages

    app.include_router(home_pages.router)

    from app.routers.pages import static_pages

    app.include_router(static_pages.router)

    from app.routers.pages import auth as auth_pages

    app.include_router(auth_pages.router)

    from app.routers.pages import catalog as catalog_pages

    app.include_router(catalog_pages.router)

    from app.routers.pages import cart as cart_pages

    app.include_router(cart_pages.router)

    from app.routers.pages import checkout as checkout_pages

    app.include_router(checkout_pages.router)

    from app.routers.pages import dashboard as dashboard_pages

    app.include_router(dashboard_pages.router)

    from app.routers.pages import admin_panel

    app.include_router(admin_panel.router)

    from app.routers.pages import warehouse as warehouse_pages

    app.include_router(warehouse_pages.router)

    # Language API
    from app.routers.api import language as language_api

    app.include_router(language_api.router)

    from app.routers.api import wishlist as wishlist_api

    app.include_router(wishlist_api.router)

    from app.routers.api import cart as cart_api

    app.include_router(cart_api.router)

    from app.routers.api import search as search_api

    app.include_router(search_api.router)

    from app.routers.api import payments as payments_api

    app.include_router(payments_api.router)

    from app.routers.api import dashboard as dashboard_api

    app.include_router(dashboard_api.router)

    from app.routers.api import stock as stock_api

    app.include_router(stock_api.router)

    from app.routers.api import warehouse as warehouse_api

    app.include_router(warehouse_api.router)

    from app.routers.api import disputes as disputes_api

    app.include_router(disputes_api.router)

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


app = create_app()

import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from app.config import settings
from app.database import async_session_factory
from app.models.user import User


async def get_user_db() -> AsyncGenerator[SQLAlchemyUserDatabase]:
    async with async_session_factory() as session:
        yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.email} registered.")

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        print(f"Password reset requested for {user.email}. Token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request=None):
        print(f"Verification requested for {user.email}. Token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


# JWT Strategy
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.jwt_secret,
        lifetime_seconds=settings.jwt_lifetime_seconds,
    )


# Cookie transport (for server-rendered pages)
cookie_transport = CookieTransport(
    cookie_name="phoenix_auth",
    cookie_max_age=settings.jwt_lifetime_seconds,
    cookie_secure=settings.is_production,
    cookie_httponly=True,
    cookie_samesite="lax",
)

# Bearer transport (for API calls)
bearer_transport = BearerTransport(tokenUrl="/api/auth/login")

# Authentication backends
cookie_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

bearer_backend = AuthenticationBackend(
    name="bearer",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [cookie_backend, bearer_backend],
)

# Dependency shortcuts
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
optional_current_user = fastapi_users.current_user(active=True, optional=True)

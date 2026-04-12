from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_language(request: Request) -> str:
    """Get current language from session, cookie, or Accept-Language header."""
    # Check session first
    lang = request.session.get("language") if hasattr(request, "session") else None
    if lang in ("id", "en"):
        return lang

    # Check cookie
    lang = request.cookies.get("language")
    if lang in ("id", "en"):
        return lang

    # Check Accept-Language header
    accept_lang = request.headers.get("accept-language", "")
    if "en" in accept_lang:
        return "en"

    # Default to Indonesian
    return "id"

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings

SUPPORTED_LANGUAGES = ("id", "en")


class I18nMiddleware(BaseHTTPMiddleware):
    """Detect and set current language for each request.

    Priority: session > cookie > Accept-Language header > default ('id')
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        language = self._detect_language(request)
        request.state.language = language
        response = await call_next(request)
        return response

    def _detect_language(self, request: Request) -> str:
        # 1. Check session
        session = getattr(request, "session", {})
        lang = session.get("language")
        if lang in SUPPORTED_LANGUAGES:
            return lang

        # 2. Check cookie
        lang = request.cookies.get("language")
        if lang in SUPPORTED_LANGUAGES:
            return lang

        # 3. Check Accept-Language header
        accept = request.headers.get("accept-language", "")
        if "en" in accept.lower():
            return "en"

        # 4. Default
        return settings.default_language

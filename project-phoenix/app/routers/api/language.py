from fastapi import APIRouter, Request
from starlette.responses import Response

router = APIRouter(prefix="/api/language", tags=["language"])


@router.post("/toggle")
async def toggle_language(request: Request):
    """Toggle between Indonesian and English."""
    current = getattr(request.state, "language", "id")
    new_lang = "en" if current == "id" else "id"

    # Store in session
    request.session["language"] = new_lang

    # Set cookie as backup
    response = Response(status_code=204)
    response.set_cookie(
        "language",
        new_lang,
        max_age=60 * 60 * 24 * 365,  # 1 year
        httponly=False,
        samesite="lax",
    )
    # Tell HTMX to refresh the page to apply language change
    response.headers["HX-Refresh"] = "true"
    return response


@router.post("/set/{language}")
async def set_language(language: str, request: Request):
    """Set language explicitly."""
    if language not in ("id", "en"):
        language = "id"

    request.session["language"] = language

    response = Response(status_code=204)
    response.set_cookie(
        "language",
        language,
        max_age=60 * 60 * 24 * 365,
        httponly=False,
        samesite="lax",
    )
    response.headers["HX-Refresh"] = "true"
    return response

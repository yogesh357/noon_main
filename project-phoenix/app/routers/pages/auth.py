from fastapi import APIRouter, Request

from app.templating import templates

router = APIRouter(prefix="/auth", tags=["auth-pages"])


@router.get("/login")
async def login_page(request: Request):
    language = getattr(request.state, "language", "id")
    return templates.TemplateResponse(
        "pages/auth/login.html",
        {"request": request, "page_title": "Login", "language": language},
    )


@router.get("/register")
async def register_page(request: Request):
    language = getattr(request.state, "language", "id")
    return templates.TemplateResponse(
        "pages/auth/register.html",
        {"request": request, "page_title": "Register", "language": language},
    )

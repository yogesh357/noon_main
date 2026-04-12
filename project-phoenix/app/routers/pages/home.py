from fastapi import APIRouter, Request

from app.templating import templates

router = APIRouter(tags=["pages"])


@router.get("/")
async def homepage(request: Request):
    language = getattr(request.state, "language", "id")
    return templates.TemplateResponse(
        "pages/home.html",
        {"request": request, "page_title": "Home", "language": language},
    )

"""Static content pages — About, T&C, FAQ, Contact, Disclaimer."""

from fastapi import APIRouter, Request

from app.templating import templates

router = APIRouter(tags=["static-pages"])


def _lang(request: Request) -> str:
    return getattr(request.state, "language", "id")


@router.get("/about")
async def about_page(request: Request):
    return templates.TemplateResponse(
        "pages/about.html",
        {"request": request, "page_title": "About Us", "language": _lang(request)},
    )


@router.get("/terms")
async def terms_page(request: Request):
    return templates.TemplateResponse(
        "pages/terms.html",
        {"request": request, "page_title": "Terms & Conditions", "language": _lang(request)},
    )


@router.get("/disclaimer")
async def disclaimer_page(request: Request):
    return templates.TemplateResponse(
        "pages/disclaimer.html",
        {"request": request, "page_title": "Disclaimer", "language": _lang(request)},
    )


@router.get("/faq")
async def faq_page(request: Request):
    return templates.TemplateResponse(
        "pages/faq.html",
        {"request": request, "page_title": "FAQ", "language": _lang(request)},
    )


@router.get("/contact")
async def contact_page(request: Request):
    return templates.TemplateResponse(
        "pages/contact.html",
        {"request": request, "page_title": "Contact Us", "language": _lang(request)},
    )

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db
from app.services.payment import handle_xendit_webhook

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/xendit/webhook")
async def xendit_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_callback_token: str | None = Header(None),
):
    """Receive Xendit payment webhook callbacks."""
    # Verify webhook token
    if settings.xendit_webhook_token and x_callback_token != settings.xendit_webhook_token:
        return JSONResponse(
            status_code=403,
            content={"error": "Invalid callback token"},
        )

    payload = await request.json()

    success = await handle_xendit_webhook(db, payload)

    if success:
        return JSONResponse(status_code=200, content={"status": "ok"})
    else:
        return JSONResponse(status_code=400, content={"error": "Unprocessable webhook"})

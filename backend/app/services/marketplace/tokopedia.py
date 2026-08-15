"""Tokopedia Developer API integration.

Docs: https://developer.tokopedia.com
Auth: OAuth 2.0 client_credentials + fs_id
"""

from app.services.marketplace.base import (
    BaseMarketplaceService,
    MarketplaceOrderData,
)


class TokopediaService(BaseMarketplaceService):
    marketplace_code = "tokopedia"

    def __init__(self):
        self.client_id = ""
        self.client_secret = ""
        self.fs_id = ""
        self.access_token = ""

    async def authenticate(self) -> bool:
        # POST https://accounts.tokopedia.com/token (client_credentials)
        return False

    async def push_product(
        self, title, description, price, stock, images, variants,
        external_id=None,
    ) -> str | None:
        # POST /v2/products/fs/{fs_id}/create or /edit
        return None

    async def update_stock(
        self, external_product_id, variant_external_id, quantity,
    ) -> bool:
        # PATCH /inventory/v1/fs/{fs_id}/stock/update
        return False

    async def pull_orders(self, since_minutes=60) -> list[MarketplaceOrderData]:
        # GET /v2/order/list?fs_id={fs_id}
        return []

    async def update_order_status(
        self, external_order_id, status, tracking_number=None,
    ) -> bool:
        # POST /v1/order/{order_id}/fs/{fs_id}/ack or /confirm-shipping
        return False

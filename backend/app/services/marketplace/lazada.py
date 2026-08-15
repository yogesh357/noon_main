"""Lazada Open Platform integration.

Docs: https://open.lazada.com
Auth: OAuth 2.0 app_key + app_secret
"""

from app.services.marketplace.base import (
    BaseMarketplaceService,
    MarketplaceOrderData,
)


class LazadaService(BaseMarketplaceService):
    marketplace_code = "lazada"

    def __init__(self):
        self.app_key = ""
        self.app_secret = ""
        self.access_token = ""

    async def authenticate(self) -> bool:
        # POST /auth/token/create (auth_code grant)
        return False

    async def push_product(
        self, title, description, price, stock, images, variants,
        external_id=None,
    ) -> str | None:
        # POST /product/create or /product/update
        return None

    async def update_stock(
        self, external_product_id, variant_external_id, quantity,
    ) -> bool:
        # POST /product/price_quantity/update
        return False

    async def pull_orders(self, since_minutes=60) -> list[MarketplaceOrderData]:
        # GET /orders/get
        return []

    async def update_order_status(
        self, external_order_id, status, tracking_number=None,
    ) -> bool:
        # POST /order/pack or /order/rts (ready to ship)
        return False

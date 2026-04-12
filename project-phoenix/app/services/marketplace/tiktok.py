"""TikTok Shop Partner Center integration.

Docs: https://partner.tiktokshop.com/developer
Auth: OAuth 2.0 app_key + app_secret
"""

from app.services.marketplace.base import (
    BaseMarketplaceService,
    MarketplaceOrderData,
)


class TikTokService(BaseMarketplaceService):
    marketplace_code = "tiktok"

    def __init__(self):
        self.app_key = ""
        self.app_secret = ""
        self.access_token = ""
        self.shop_id = ""

    async def authenticate(self) -> bool:
        # POST /api/v2/token/get (auth_code grant)
        return False

    async def push_product(
        self, title, description, price, stock, images, variants,
        external_id=None,
    ) -> str | None:
        # POST /api/products or PUT /api/products/{product_id}
        return None

    async def update_stock(
        self, external_product_id, variant_external_id, quantity,
    ) -> bool:
        # PUT /api/products/stocks
        return False

    async def pull_orders(self, since_minutes=60) -> list[MarketplaceOrderData]:
        # POST /api/orders/search
        return []

    async def update_order_status(
        self, external_order_id, status, tracking_number=None,
    ) -> bool:
        # POST /api/orders/{order_id}/shipping_info
        return False

"""Shopee Open Platform integration.

Docs: https://open.shopee.com/documents
Auth: OAuth 2.0 via partner_id + shop_id
"""

import hashlib
import hmac

from app.services.marketplace.base import (
    BaseMarketplaceService,
    MarketplaceOrderData,
)

SHOPEE_BASE_URL = "https://partner.shopeemobile.com/api/v2"


class ShopeeService(BaseMarketplaceService):
    marketplace_code = "shopee"

    def __init__(self):
        self.partner_id = ""  # From settings when configured
        self.partner_key = ""
        self.shop_id = ""
        self.access_token = ""

    def _sign(self, path: str, timestamp: int) -> str:
        """Generate HMAC-SHA256 signature for Shopee API."""
        base_string = f"{self.partner_id}{path}{timestamp}{self.access_token}{self.shop_id}"
        return hmac.new(
            self.partner_key.encode(),
            base_string.encode(),
            hashlib.sha256,
        ).hexdigest()

    async def authenticate(self) -> bool:
        # OAuth token refresh via Shopee auth endpoint
        # Requires initial auth code from shop authorization flow
        return False  # Placeholder until API keys configured

    async def push_product(
        self, title, description, price, stock, images, variants,
        external_id=None,
    ) -> str | None:
        # Shopee: POST /product/add_item or /product/update_item
        return None  # Placeholder

    async def update_stock(
        self, external_product_id, variant_external_id, quantity,
    ) -> bool:
        # Shopee: POST /product/update_stock
        return False  # Placeholder

    async def pull_orders(self, since_minutes=60) -> list[MarketplaceOrderData]:
        # Shopee: GET /order/get_order_list
        return []  # Placeholder

    async def update_order_status(
        self, external_order_id, status, tracking_number=None,
    ) -> bool:
        # Shopee: POST /logistics/ship_order
        return False  # Placeholder

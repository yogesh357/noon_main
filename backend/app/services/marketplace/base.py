"""Abstract base for marketplace integrations (Shopee, Tokopedia, TikTok, Lazada)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class MarketplaceProduct:
    external_id: str
    title: str
    description: str
    price: float
    stock: int
    images: list[str] = field(default_factory=list)
    variants: list[dict] = field(default_factory=list)


@dataclass
class MarketplaceOrderData:
    external_order_id: str
    marketplace: str
    buyer_name: str
    buyer_phone: str
    shipping_address: dict
    items: list[dict]
    total: float
    raw_data: dict


class BaseMarketplaceService(ABC):
    """Abstract interface for marketplace integrations.

    Each marketplace (Shopee, Tokopedia, TikTok Shop, Lazada) implements this.
    All methods are async for non-blocking API calls via httpx.
    """

    marketplace_code: str = ""

    @abstractmethod
    async def authenticate(self) -> bool:
        """Refresh OAuth 2.0 token. Returns True if successful."""

    @abstractmethod
    async def push_product(
        self,
        title: str,
        description: str,
        price: float,
        stock: int,
        images: list[str],
        variants: list[dict],
        external_id: str | None = None,
    ) -> str | None:
        """Push/update a product to the marketplace. Returns external product ID."""

    @abstractmethod
    async def update_stock(
        self,
        external_product_id: str,
        variant_external_id: str | None,
        quantity: int,
    ) -> bool:
        """Update stock level for a product/variant on the marketplace."""

    @abstractmethod
    async def pull_orders(
        self,
        since_minutes: int = 60,
    ) -> list[MarketplaceOrderData]:
        """Pull new orders from the marketplace."""

    @abstractmethod
    async def update_order_status(
        self,
        external_order_id: str,
        status: str,
        tracking_number: str | None = None,
    ) -> bool:
        """Update order status on the marketplace (e.g., shipped with tracking)."""

"""Abstract base for courier integrations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ShippingRate:
    courier: str
    service: str
    cost: float
    estimated_days: str
    description: str = ""


@dataclass
class ShipmentResult:
    tracking_number: str
    courier: str
    label_url: str | None = None


@dataclass
class TrackingEventData:
    status: str
    description: str
    location: str | None
    timestamp: str
    raw_data: dict | None = None


class BaseCourierService(ABC):
    """Abstract interface for courier integrations.

    Each courier (JNE, J&T, SiCepat, etc.) implements this interface.
    A factory function selects the right service based on courier code.
    """

    @abstractmethod
    async def get_rates(
        self,
        origin_city_id: str,
        destination_city_id: str,
        weight_grams: int,
    ) -> list[ShippingRate]:
        """Get available shipping rates between two cities."""

    @abstractmethod
    async def create_shipment(
        self,
        order_number: str,
        sender: dict,
        recipient: dict,
        weight_grams: int,
        items: list[dict],
    ) -> ShipmentResult:
        """Book a shipment and get tracking number."""

    @abstractmethod
    async def get_tracking(
        self,
        tracking_number: str,
        courier: str = "",
    ) -> list[TrackingEventData]:
        """Get tracking events for a shipment."""

    @abstractmethod
    async def cancel_shipment(
        self,
        tracking_number: str,
    ) -> bool:
        """Cancel a shipment. Returns True if successful."""

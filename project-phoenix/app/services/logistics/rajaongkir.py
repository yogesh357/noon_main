"""RajaOngkir API client — unified rate checking and tracking for Indonesian couriers.

Docs: https://rajaongkir.com/dokumentasi
Pro account (~$10/month) supports all couriers and waybill tracking.
"""

import httpx

from app.config import settings
from app.services.logistics.base import (
    BaseCourierService,
    ShipmentResult,
    ShippingRate,
    TrackingEventData,
)

RAJAONGKIR_BASE_URL = "https://pro.rajaongkir.com/api"

# Status normalization map: RajaOngkir status → our unified status
STATUS_MAP = {
    "MANIFESTED": "label_created",
    "PICKUP": "picked_up",
    "ON PROCESS": "in_transit",
    "IN TRANSIT": "in_transit",
    "RECEIVED ON DESTINATION": "in_transit",
    "ON DELIVERY": "out_for_delivery",
    "DELIVERED": "delivered",
    "RETURNED": "returned",
    "PROBLEM": "exception",
}


class RajaOngkirService(BaseCourierService):
    """RajaOngkir Pro API — rate checking + waybill tracking."""

    def __init__(self):
        self.api_key = settings.rajaongkir_api_key
        self.headers = {"key": self.api_key}

    async def get_rates(
        self,
        origin_city_id: str,
        destination_city_id: str,
        weight_grams: int,
    ) -> list[ShippingRate]:
        """Get shipping rates from all supported couriers."""
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{RAJAONGKIR_BASE_URL}/cost",
                headers=self.headers,
                data={
                    "origin": origin_city_id,
                    "originType": "city",
                    "destination": destination_city_id,
                    "destinationType": "city",
                    "weight": weight_grams,
                    "courier": "jne:jnt:tiki:sicepat",
                },
            )

        if response.status_code != 200:
            return []

        data = response.json()
        results = data.get("rajaongkir", {}).get("results", [])

        rates = []
        for courier_data in results:
            courier_code = courier_data.get("code", "").lower()
            for cost_item in courier_data.get("costs", []):
                service = cost_item.get("service", "")
                for detail in cost_item.get("cost", []):
                    rates.append(ShippingRate(
                        courier=courier_code,
                        service=service,
                        cost=detail.get("value", 0),
                        estimated_days=detail.get("etd", ""),
                        description=cost_item.get("description", ""),
                    ))

        return rates

    async def create_shipment(
        self,
        order_number: str,
        sender: dict,
        recipient: dict,
        weight_grams: int,
        items: list[dict],
    ) -> ShipmentResult:
        """RajaOngkir doesn't support shipment booking.

        Booking must be done via individual courier APIs or Biteship.
        This returns a placeholder — actual tracking number must be
        set via admin or courier API integration.
        """
        return ShipmentResult(
            tracking_number=f"PENDING-{order_number}",
            courier="pending",
            label_url=None,
        )

    async def get_tracking(
        self,
        tracking_number: str,
        courier: str = "jne",
    ) -> list[TrackingEventData]:
        """Get tracking/waybill info via RajaOngkir Pro."""
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{RAJAONGKIR_BASE_URL}/waybill",
                headers=self.headers,
                data={
                    "waybill": tracking_number,
                    "courier": courier,
                },
            )

        if response.status_code != 200:
            return []

        data = response.json()
        waybill = data.get("rajaongkir", {}).get("result", {})
        manifest = waybill.get("manifest", [])

        events = []
        for entry in manifest:
            raw_status = entry.get("manifest_description", "")
            normalized = self._normalize_status(raw_status)

            events.append(TrackingEventData(
                status=normalized,
                description=entry.get("manifest_description", ""),
                location=entry.get("city_name"),
                timestamp=f"{entry.get('manifest_date', '')} {entry.get('manifest_time', '')}",
                raw_data=entry,
            ))

        return events

    async def cancel_shipment(self, tracking_number: str) -> bool:
        """RajaOngkir doesn't support cancellation."""
        return False

    def _normalize_status(self, raw_status: str) -> str:
        """Map courier-specific status to unified status."""
        upper = raw_status.upper()
        for key, value in STATUS_MAP.items():
            if key in upper:
                return value
        return "in_transit"


# --- Convenience functions ---

async def get_shipping_rates(
    origin_city_id: str,
    destination_city_id: str,
    weight_grams: int,
) -> list[ShippingRate]:
    """Get rates from RajaOngkir."""
    service = RajaOngkirService()
    return await service.get_rates(origin_city_id, destination_city_id, weight_grams)


async def get_waybill_tracking(
    tracking_number: str,
    courier: str,
) -> list[TrackingEventData]:
    """Get tracking events from RajaOngkir."""
    service = RajaOngkirService()
    return await service.get_tracking(tracking_number, courier)

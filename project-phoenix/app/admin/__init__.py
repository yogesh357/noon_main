from fastapi import FastAPI
from sqladmin import Admin

from app.database import engine


def setup_admin(app: FastAPI) -> None:
    admin = Admin(app, engine, title="Noon Admin")

    from app.admin.views import (
        AddressAdmin,
        CategoryAdmin,
        DisputeAdmin,
        DisputeEvidenceAdmin,
        MarketplaceListingAdmin,
        MarketplaceOrderAdmin,
        NotificationAdmin,
        OrderAdmin,
        PaymentAdmin,
        ProductAdmin,
        ProductImageAdmin,
        ProductVariantAdmin,
        ReviewAdmin,
        ShipmentAdmin,
        SyncLogAdmin,
        TrackingEventAdmin,
        UserAdmin,
        WishlistAdmin,
    )

    admin.add_view(UserAdmin)
    admin.add_view(AddressAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(ProductVariantAdmin)
    admin.add_view(ProductImageAdmin)
    admin.add_view(ReviewAdmin)
    admin.add_view(WishlistAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(PaymentAdmin)
    admin.add_view(NotificationAdmin)
    admin.add_view(ShipmentAdmin)
    admin.add_view(TrackingEventAdmin)
    admin.add_view(MarketplaceListingAdmin)
    admin.add_view(MarketplaceOrderAdmin)
    admin.add_view(SyncLogAdmin)
    admin.add_view(DisputeAdmin)
    admin.add_view(DisputeEvidenceAdmin)

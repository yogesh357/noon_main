from sqladmin import ModelView

from app.models.catalog import Category, Product, ProductImage, ProductVariant, Review
from app.models.dispute import Dispute, DisputeEvidence
from app.models.logistics import Shipment, TrackingEvent
from app.models.marketplace import MarketplaceListing, MarketplaceOrder, SyncLog
from app.models.notification import Notification
from app.models.order import Order, Payment
from app.models.user import Address, User
from app.models.wishlist import Wishlist


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id, User.email, User.full_name,
        User.role, User.is_active, User.created_at,
    ]
    column_searchable_list = [User.email, User.full_name]
    column_sortable_list = [User.email, User.created_at, User.role]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class AddressAdmin(ModelView, model=Address):
    column_list = [
        Address.id, Address.user_id, Address.full_name,
        Address.city, Address.is_default,
    ]
    column_searchable_list = [Address.full_name, Address.city]
    can_create = True
    can_edit = True
    can_delete = True
    name = "Address"
    name_plural = "Addresses"
    icon = "fa-solid fa-location-dot"


class CategoryAdmin(ModelView, model=Category):
    column_list = [
        Category.id, Category.name_en, Category.slug,
        Category.parent_id, Category.sort_order, Category.is_active,
    ]
    column_searchable_list = [Category.name_en, Category.name_id]
    column_sortable_list = [Category.sort_order, Category.name_en]
    column_default_sort = "sort_order"
    name = "Category"
    name_plural = "Categories"
    icon = "fa-solid fa-folder"


class ProductAdmin(ModelView, model=Product):
    column_list = [
        Product.id, Product.name_en, Product.brand,
        Product.base_price, Product.is_active, Product.created_at,
    ]
    column_searchable_list = [Product.name_en, Product.name_id, Product.brand]
    column_sortable_list = [Product.name_en, Product.base_price, Product.created_at]
    column_default_sort = ("created_at", True)
    name = "Product"
    name_plural = "Products"
    icon = "fa-solid fa-box"


class ProductVariantAdmin(ModelView, model=ProductVariant):
    column_list = [
        ProductVariant.id, ProductVariant.product_id, ProductVariant.sku,
        ProductVariant.size, ProductVariant.color,
        ProductVariant.stock_quantity, ProductVariant.is_active,
    ]
    column_searchable_list = [ProductVariant.sku, ProductVariant.barcode]
    column_sortable_list = [ProductVariant.sku, ProductVariant.stock_quantity]
    name = "Variant"
    name_plural = "Variants"
    icon = "fa-solid fa-cubes"


class ProductImageAdmin(ModelView, model=ProductImage):
    column_list = [
        ProductImage.id, ProductImage.product_id, ProductImage.image_url,
        ProductImage.sort_order, ProductImage.is_primary,
    ]
    name = "Image"
    name_plural = "Images"
    icon = "fa-solid fa-image"


class ReviewAdmin(ModelView, model=Review):
    column_list = [
        Review.id, Review.product_id, Review.user_id,
        Review.rating, Review.is_verified_purchase, Review.created_at,
    ]
    column_sortable_list = [Review.rating, Review.created_at]
    column_default_sort = ("created_at", True)
    name = "Review"
    name_plural = "Reviews"
    icon = "fa-solid fa-star"


class WishlistAdmin(ModelView, model=Wishlist):
    column_list = [
        Wishlist.id, Wishlist.user_id, Wishlist.product_id, Wishlist.created_at,
    ]
    name = "Wishlist"
    name_plural = "Wishlists"
    icon = "fa-solid fa-heart"


class OrderAdmin(ModelView, model=Order):
    column_list = [
        Order.id, Order.order_number, Order.status, Order.source,
        Order.total, Order.courier, Order.created_at,
    ]
    column_searchable_list = [Order.order_number]
    column_sortable_list = [
        Order.order_number, Order.status, Order.total, Order.created_at,
    ]
    column_default_sort = ("created_at", True)
    name = "Order"
    name_plural = "Orders"
    icon = "fa-solid fa-shopping-bag"


class PaymentAdmin(ModelView, model=Payment):
    column_list = [
        Payment.id, Payment.order_id, Payment.xendit_invoice_id,
        Payment.method, Payment.status, Payment.amount, Payment.paid_at,
    ]
    column_searchable_list = [Payment.xendit_invoice_id]
    column_sortable_list = [Payment.status, Payment.amount, Payment.created_at]
    column_default_sort = ("created_at", True)
    name = "Payment"
    name_plural = "Payments"
    icon = "fa-solid fa-credit-card"


class NotificationAdmin(ModelView, model=Notification):
    column_list = [
        Notification.id, Notification.user_id, Notification.type,
        Notification.title_en, Notification.is_read, Notification.created_at,
    ]
    column_sortable_list = [Notification.created_at, Notification.is_read]
    column_default_sort = ("created_at", True)
    name = "Notification"
    name_plural = "Notifications"
    icon = "fa-solid fa-bell"


class ShipmentAdmin(ModelView, model=Shipment):
    column_list = [
        Shipment.id, Shipment.order_id, Shipment.courier,
        Shipment.tracking_number, Shipment.status, Shipment.created_at,
    ]
    column_searchable_list = [Shipment.tracking_number]
    column_sortable_list = [Shipment.status, Shipment.created_at]
    column_default_sort = ("created_at", True)
    name = "Shipment"
    name_plural = "Shipments"
    icon = "fa-solid fa-truck"


class TrackingEventAdmin(ModelView, model=TrackingEvent):
    column_list = [
        TrackingEvent.id, TrackingEvent.shipment_id, TrackingEvent.status,
        TrackingEvent.description, TrackingEvent.location, TrackingEvent.timestamp,
    ]
    column_sortable_list = [TrackingEvent.timestamp]
    column_default_sort = ("timestamp", True)
    name = "Tracking Event"
    name_plural = "Tracking Events"
    icon = "fa-solid fa-route"


class MarketplaceListingAdmin(ModelView, model=MarketplaceListing):
    column_list = [
        MarketplaceListing.id, MarketplaceListing.product_id,
        MarketplaceListing.marketplace, MarketplaceListing.external_product_id,
        MarketplaceListing.sync_status, MarketplaceListing.last_synced_at,
    ]
    column_searchable_list = [MarketplaceListing.external_product_id]
    column_sortable_list = [MarketplaceListing.last_synced_at]
    name = "Marketplace Listing"
    name_plural = "Marketplace Listings"
    icon = "fa-solid fa-store"


class MarketplaceOrderAdmin(ModelView, model=MarketplaceOrder):
    column_list = [
        MarketplaceOrder.id, MarketplaceOrder.external_order_id,
        MarketplaceOrder.marketplace, MarketplaceOrder.linked_order_id,
        MarketplaceOrder.status, MarketplaceOrder.created_at,
    ]
    column_searchable_list = [MarketplaceOrder.external_order_id]
    column_sortable_list = [MarketplaceOrder.created_at]
    column_default_sort = ("created_at", True)
    name = "Marketplace Order"
    name_plural = "Marketplace Orders"
    icon = "fa-solid fa-cart-shopping"


class SyncLogAdmin(ModelView, model=SyncLog):
    column_list = [
        SyncLog.id, SyncLog.marketplace, SyncLog.action,
        SyncLog.status, SyncLog.created_at,
    ]
    column_sortable_list = [SyncLog.created_at]
    column_default_sort = ("created_at", True)
    can_create = False
    can_edit = False
    name = "Sync Log"
    name_plural = "Sync Logs"
    icon = "fa-solid fa-arrows-rotate"


class DisputeAdmin(ModelView, model=Dispute):
    column_list = [
        Dispute.id, Dispute.order_id, Dispute.type,
        Dispute.reason, Dispute.status, Dispute.sla_deadline, Dispute.opened_at,
    ]
    column_sortable_list = [Dispute.opened_at, Dispute.sla_deadline, Dispute.status]
    column_default_sort = ("opened_at", True)
    name = "Dispute"
    name_plural = "Disputes"
    icon = "fa-solid fa-triangle-exclamation"


class DisputeEvidenceAdmin(ModelView, model=DisputeEvidence):
    column_list = [
        DisputeEvidence.id, DisputeEvidence.dispute_id,
        DisputeEvidence.file_url, DisputeEvidence.uploaded_at,
    ]
    column_default_sort = ("uploaded_at", True)
    name = "Dispute Evidence"
    name_plural = "Dispute Evidence"
    icon = "fa-solid fa-file-image"

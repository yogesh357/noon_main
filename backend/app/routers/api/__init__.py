from fastapi import APIRouter

from app.routers.api.catalog import router as catalog_router
from app.routers.api.cart import router as cart_router
from app.routers.api.checkout import router as checkout_router
from app.routers.api.dashboard import router as dashboard_router
from app.routers.api.admin import router as admin_router
from app.routers.api.warehouse import router as warehouse_router

router = APIRouter()

router.include_router(catalog_router)
router.include_router(cart_router)
router.include_router(checkout_router)
router.include_router(dashboard_router)
router.include_router(admin_router)
router.include_router(warehouse_router)

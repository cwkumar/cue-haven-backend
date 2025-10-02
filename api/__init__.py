from .admin import auth_router, admin_router
from .inventory import router as inventory_router

__all__ = ["auth_router", "admin_router", "inventory_router"]

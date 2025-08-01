from .health import router as health_router
from .teams import router as teams_router
from .spaces import router as spaces_router

__all__ = ["health_router", "teams_router", "spaces_router"] 
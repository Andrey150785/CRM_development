from .projects import router as project_router
from .objects import router as object_router
from .users import router as user_router
from .deals import router as deal_router

__all__ = ["project_router", "object_router", "user_router", "deal_router"]
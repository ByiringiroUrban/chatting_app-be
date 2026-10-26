from app.routers.auth import router as auth_router
from app.routers.conversations import router as conversations_router
from app.routers.messages import router as messages_router
from app.routers.groups import router as groups_router
from app.routers.statuses import router as statuses_router
from app.routers.channels import router as channels_router
from app.routers.business import router as business_router
from app.routers.calls import router as calls_router
from app.routers.ads import router as ads_router
from app.routers.subscriptions import router as subscriptions_router
from app.routers.upload import router as upload_router

__all__ = [
    "auth_router",
    "conversations_router",
    "messages_router",
    "groups_router",
    "statuses_router",
    "channels_router",
    "business_router",
    "calls_router",
    "ads_router",
    "subscriptions_router",
    "upload_router",
]

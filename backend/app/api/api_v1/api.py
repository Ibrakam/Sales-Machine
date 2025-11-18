"""
Главный роутер API v1
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    ai,
    auth,
    calls,
    crm,
    forecasts,
    instagram,
    leads,
    messages,
    users,
)

api_router = APIRouter()

# Подключение всех endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(crm.router, prefix="/crm", tags=["crm"])
api_router.include_router(forecasts.router, prefix="/forecasts", tags=["forecasts"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(instagram.router, prefix="/instagram", tags=["instagram"])

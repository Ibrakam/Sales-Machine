"""
Pydantic схемы для валидации данных
"""
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.lead import Lead, LeadCreate, LeadUpdate, LeadInDB
from app.schemas.lead_interaction import LeadInteraction, LeadInteractionCreate
from app.schemas.message import Message, MessageCreate, MessageUpdate
from app.schemas.auth import Token, TokenPayload, LoginRequest
from app.schemas.crm_connection import CRMConnection, CRMConnectionCreate, CRMConnectionUpdate
from app.schemas.forecast import Forecast, ForecastCreate, ForecastUpdate
from app.schemas.call import Call, CallCreate, CallTranscript, CallTask
from app.schemas.instagram import (
    InstagramAccount,
    InstagramAccountCreate,
    InstagramAccountUpdate,
    InstagramSyncResponse,
)

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Lead", "LeadCreate", "LeadUpdate", "LeadInDB",
    "LeadInteraction", "LeadInteractionCreate",
    "Message", "MessageCreate", "MessageUpdate",
    "Token", "TokenPayload", "LoginRequest",
    "CRMConnection", "CRMConnectionCreate", "CRMConnectionUpdate",
    "InstagramAccount", "InstagramAccountCreate", "InstagramAccountUpdate", "InstagramSyncResponse",
    "Forecast", "ForecastCreate", "ForecastUpdate",
    "Call", "CallCreate", "CallTranscript", "CallTask"
]

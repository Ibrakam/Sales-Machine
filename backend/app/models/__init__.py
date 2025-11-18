"""
Модели базы данных
"""
from app.core.database import Base
from app.models.user import User
from app.models.lead import Lead
from app.models.lead_interaction import LeadInteraction
from app.models.message import Message
from app.models.instagram_account import InstagramAccount
from app.models.crm_connection import CRMConnection
from app.models.forecast import Forecast
from app.models.call import Call, CallTranscript, CallTask
from app.models.phone_number import PhoneNumber

__all__ = [
    "Base",
    "User", 
    "Lead",
    "LeadInteraction",
    "Message",
    "InstagramAccount",
    "CRMConnection",
    "Forecast",
    "Call",
    "CallTranscript", 
    "CallTask",
    "PhoneNumber"
]

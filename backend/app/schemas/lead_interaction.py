"""
Схемы для истории взаимодействий с лидом
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class InteractionAuthor(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"
    AI = "ai"


class LeadInteractionBase(BaseModel):
    author_type: InteractionAuthor = InteractionAuthor.ADMIN
    message: str = Field(..., min_length=1, max_length=5000)
    author_name: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class LeadInteractionCreate(LeadInteractionBase):
    pass


class LeadInteraction(LeadInteractionBase):
    id: int
    lead_id: int
    created_at: datetime

    class Config:
        from_attributes = True

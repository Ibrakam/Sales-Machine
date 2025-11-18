"""
Схемы для лидов
"""
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class LeadStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class LeadSource(str, Enum):
    WEBSITE = "website"
    SOCIAL = "social"
    CALL = "call"
    OTHER = "other"


class LeadBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    position: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    source: Optional[LeadSource] = LeadSource.WEBSITE
    source_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    assigned_to: Optional[int] = None
    status: LeadStatus = LeadStatus.NEW


class LeadUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    position: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    status: Optional[LeadStatus] = None
    score: Optional[float] = Field(None, ge=0, le=100)
    score_category: Optional[str] = None
    source: Optional[LeadSource] = None
    assigned_to: Optional[int] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    next_follow_up: Optional[datetime] = None


class LeadInDB(LeadBase):
    id: int
    status: LeadStatus
    score: float
    score_category: str
    assigned_to: Optional[int] = None
    crm_id: Optional[str] = None
    crm_type: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_contacted: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None

    class Config:
        from_attributes = True


class Lead(LeadInDB):
    pass


class LeadWithUser(Lead):
    """Лид с информацией о назначенном пользователе"""
    assigned_to_user: Optional[Dict[str, Any]] = None


class LeadList(BaseModel):
    """Список лидов с пагинацией"""
    items: List[Lead]
    total: int
    page: int
    size: int
    pages: int

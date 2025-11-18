"""
Схемы для интеграции с Instagram
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.lead import Lead


class InstagramAccountBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=150)
    business_account_id: Optional[str] = Field(None, max_length=255)
    profile_url: Optional[str] = Field(None, max_length=500)
    followers_count: Optional[int] = Field(None, ge=0)
    integration_metadata: Optional[Dict[str, Any]] = None


class InstagramAccountCreate(InstagramAccountBase):
    access_token: Optional[str] = None


class InstagramAccountUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=150)
    business_account_id: Optional[str] = Field(None, max_length=255)
    profile_url: Optional[str] = Field(None, max_length=500)
    followers_count: Optional[int] = Field(None, ge=0)
    access_token: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|connected|disconnected)$")
    integration_metadata: Optional[Dict[str, Any]] = None


class InstagramAccount(InstagramAccountBase):
    id: int
    status: str
    connected_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InstagramSyncResponse(BaseModel):
    synced: int
    created_leads: List[Lead] = []

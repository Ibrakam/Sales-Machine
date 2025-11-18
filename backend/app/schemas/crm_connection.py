"""
Схемы для CRM подключений
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CRMConnectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    crm_type: str = Field(..., min_length=1, max_length=50)
    org_name: Optional[str] = None
    sync_leads: bool = True
    sync_contacts: bool = True
    sync_deals: bool = True
    sync_companies: bool = True
    sync_direction: str = "bidirectional"


class CRMConnectionCreate(CRMConnectionBase):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    org_id: Optional[str] = None
    field_mapping: Optional[Dict[str, Any]] = None


class CRMConnectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    org_name: Optional[str] = None
    is_active: Optional[bool] = None
    sync_leads: Optional[bool] = None
    sync_contacts: Optional[bool] = None
    sync_deals: Optional[bool] = None
    sync_companies: Optional[bool] = None
    sync_direction: Optional[str] = None
    field_mapping: Optional[Dict[str, Any]] = None


class CRMConnectionInDB(CRMConnectionBase):
    id: int
    org_id: Optional[str] = None
    is_active: bool
    last_sync_at: Optional[datetime] = None
    sync_count: int
    error_count: int
    last_error: Optional[str] = None
    field_mapping: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CRMConnection(CRMConnectionInDB):
    pass


class CRMConnectionList(BaseModel):
    """Список CRM подключений"""
    items: list[CRMConnection]
    total: int

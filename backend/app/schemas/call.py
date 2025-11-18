"""
Схемы для звонков
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.call import CallDirection, CallStatus


class CallBase(BaseModel):
    lead_id: Optional[int] = None
    from_number: str = Field(..., min_length=1, max_length=20)
    to_number: str = Field(..., min_length=1, max_length=20)
    direction: CallDirection


class CallCreate(CallBase):
    pass


class CallUpdate(BaseModel):
    status: Optional[CallStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    recording_url: Optional[str] = None
    recording_duration: Optional[int] = None
    consent_given: Optional[bool] = None
    external_call_id: Optional[str] = None
    provider: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class CallInDB(CallBase):
    id: int
    agent_id: int
    status: CallStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    recording_url: Optional[str] = None
    recording_duration: Optional[int] = None
    consent_given: bool
    external_call_id: Optional[str] = None
    provider: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Call(CallInDB):
    pass


class CallWithLead(Call):
    """Звонок с информацией о лиде"""
    lead: Optional[Dict[str, Any]] = None


class CallTranscriptBase(BaseModel):
    language: str = "de"
    text: Optional[str] = None


class CallTranscriptCreate(CallTranscriptBase):
    call_id: int


class CallTranscriptUpdate(BaseModel):
    text: Optional[str] = None
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    sentiment_label: Optional[str] = None
    summary: Optional[str] = None
    intents: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    entities: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    quality_score: Optional[float] = Field(None, ge=0, le=1)


class CallTranscriptInDB(CallTranscriptBase):
    id: int
    call_id: int
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    summary: Optional[str] = None
    intents: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    entities: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    quality_score: Optional[float] = None
    processing_time: Optional[float] = None
    model_used: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CallTranscript(CallTranscriptInDB):
    pass


class CallTaskBase(BaseModel):
    lead_id: int
    task_type: str = Field(..., min_length=1, max_length=50)
    reason: Optional[str] = None
    priority: str = "medium"
    due_at: datetime
    assigned_to: Optional[int] = None


class CallTaskCreate(CallTaskBase):
    pass


class CallTaskUpdate(BaseModel):
    task_type: Optional[str] = Field(None, min_length=1, max_length=50)
    reason: Optional[str] = None
    priority: Optional[str] = None
    due_at: Optional[datetime] = None
    assigned_to: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class CallTaskInDB(CallTaskBase):
    id: int
    created_by: int
    status: str
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CallTask(CallTaskInDB):
    pass


class CallList(BaseModel):
    """Список звонков с пагинацией"""
    items: List[Call]
    total: int
    page: int
    size: int
    pages: int

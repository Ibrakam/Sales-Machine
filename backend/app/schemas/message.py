"""
Схемы для сообщений
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.message import MessageType, MessageStatus


class MessageBase(BaseModel):
    lead_id: int
    message_type: MessageType
    subject: Optional[str] = Field(None, max_length=500)
    body: str = Field(..., min_length=1)
    language: str = "de"


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    subject: Optional[str] = Field(None, max_length=500)
    body: Optional[str] = Field(None, min_length=1)
    language: Optional[str] = None
    status: Optional[MessageStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageInDB(MessageBase):
    id: int
    created_by: int
    status: MessageStatus
    is_ai_generated: bool
    ai_prompt: Optional[str] = None
    ai_model: Optional[str] = None
    ai_tokens_used: Optional[int] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    external_id: Optional[str] = None
    thread_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Message(MessageInDB):
    pass


class MessageWithLead(Message):
    """Сообщение с информацией о лиде"""
    lead: Optional[Dict[str, Any]] = None


class MessageList(BaseModel):
    """Список сообщений с пагинацией"""
    items: list[Message]
    total: int
    page: int
    size: int
    pages: int

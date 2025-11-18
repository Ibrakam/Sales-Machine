"""
Модель сообщений
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MessageType(str, enum.Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    CALL = "call"


class MessageStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    FAILED = "failed"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    
    # Связи
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Тип и статус
    message_type = Column(Enum(MessageType), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.DRAFT)
    
    # Содержимое
    subject = Column(String(500), nullable=True)
    body = Column(Text, nullable=False)
    language = Column(String(10), default="de")  # de, en
    
    # AI генерация
    is_ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text, nullable=True)
    ai_model = Column(String(100), nullable=True)
    ai_tokens_used = Column(Integer, nullable=True)
    
    # Отправка
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    
    # Внешние ID
    external_id = Column(String(255), nullable=True)  # ID в внешней системе
    thread_id = Column(String(255), nullable=True)  # ID треда для email
    
    # Метаданные
    message_metadata = Column(JSON, nullable=True)  # Дополнительные данные
    error_message = Column(Text, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    lead = relationship("Lead", back_populates="messages")
    created_by_user = relationship("User", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, type='{self.message_type}', status='{self.status}')>"

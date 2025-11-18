"""
Модели для телефонии
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class CallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallStatus(str, enum.Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"


class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    
    # Связи
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Номера телефонов
    from_number = Column(String(20), nullable=False)
    to_number = Column(String(20), nullable=False)
    
    # Направление и статус
    direction = Column(Enum(CallDirection), nullable=False)
    status = Column(Enum(CallStatus), default=CallStatus.INITIATED)
    
    # Временные метки
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Запись
    recording_url = Column(String(1000), nullable=True)
    recording_duration = Column(Integer, nullable=True)
    consent_given = Column(Boolean, default=False)
    
    # Внешние ID
    external_call_id = Column(String(255), nullable=True)  # ID в телефонии провайдера
    provider = Column(String(50), nullable=True)  # twilio, vonage, etc.
    
    # Метаданные
    call_metadata = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    lead = relationship("Lead", back_populates="calls")
    agent = relationship("User", back_populates="calls")
    transcript = relationship("CallTranscript", back_populates="call", uselist=False)
    
    def __repr__(self):
        return f"<Call(id={self.id}, direction='{self.direction}', status='{self.status}')>"


class CallTranscript(Base):
    __tablename__ = "call_transcripts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Связь с звонком
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    
    # Транскрипт
    language = Column(String(10), default="de")
    text = Column(Text, nullable=True)
    
    # AI анализ
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    sentiment_label = Column(String(20), nullable=True)  # positive, negative, neutral
    summary = Column(Text, nullable=True)
    
    # Извлеченная информация
    intents = Column(JSON, nullable=True)  # ["interested", "objection", "meeting_request"]
    keywords = Column(JSON, nullable=True)  # ["price", "competitor", "timeline"]
    entities = Column(JSON, nullable=True)  # {"person": "John", "company": "ABC Corp"}
    
    # Качество
    confidence_score = Column(Float, nullable=True)  # 0-1
    quality_score = Column(Float, nullable=True)  # 0-1
    
    # Метаданные
    processing_time = Column(Float, nullable=True)  # секунды
    model_used = Column(String(100), nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    call = relationship("Call", back_populates="transcript")
    
    def __repr__(self):
        return f"<CallTranscript(id={self.id}, call_id={self.call_id}, sentiment='{self.sentiment_label}')>"


class CallTask(Base):
    __tablename__ = "call_tasks"

    id = Column(Integer, primary_key=True, index=True)
    
    # Связи
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Задача
    task_type = Column(String(50), nullable=False)  # callback, follow_up, meeting
    reason = Column(String(255), nullable=True)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Время
    due_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Статус
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    
    # Метаданные
    notes = Column(Text, nullable=True)
    task_metadata = Column(JSON, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<CallTask(id={self.id}, type='{self.task_type}', due='{self.due_at}')>"

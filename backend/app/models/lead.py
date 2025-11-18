"""
Модель лида
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(255), nullable=False)
    email = Column(String(255), index=True, nullable=True)
    phone = Column(String(20), nullable=True)
    company = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Адрес
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # Бизнес информация
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)  # 1-10, 11-50, 51-200, 201-1000, 1000+
    annual_revenue = Column(String(50), nullable=True)
    
    # Статус и скоринг
    status = Column(String(50), default="new")  # new, in_progress, completed
    score = Column(Float, default=0.0)  # 0-100
    score_category = Column(String(20), default="cold")  # hot, warm, cold
    
    # Источник
    source = Column(String(100), nullable=True)  # website, social, call, event, referral
    source_data = Column(JSON, nullable=True)  # Дополнительные данные об источнике
    
    # Назначение
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Теги и метаданные
    tags = Column(JSON, nullable=True)  # ["enterprise", "saas", "startup"]
    custom_fields = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    
    # CRM интеграция
    crm_id = Column(String(100), nullable=True)  # ID в внешней CRM
    crm_type = Column(String(50), nullable=True)  # hubspot, pipedrive, salesforce
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_contacted = Column(DateTime(timezone=True), nullable=True)
    next_follow_up = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    assigned_to_user = relationship("User", back_populates="leads")
    messages = relationship("Message", back_populates="lead")
    calls = relationship("Call", back_populates="lead")
    interactions = relationship(
        "LeadInteraction",
        back_populates="lead",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.name}', company='{self.company}', score={self.score})>"

"""
Модель телефонных номеров
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True, index=True)
    
    # Номер телефона
    e164 = Column(String(20), unique=True, nullable=False)  # +49123456789
    country = Column(String(10), nullable=False)  # DE, US, etc.
    area_code = Column(String(10), nullable=True)
    local_number = Column(String(20), nullable=True)
    
    # Назначение
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Провайдер
    provider = Column(String(50), nullable=True)  # twilio, vonage, etc.
    provider_id = Column(String(255), nullable=True)  # ID у провайдера
    
    # Настройки
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    can_receive_calls = Column(Boolean, default=True)
    can_make_calls = Column(Boolean, default=True)
    
    # Функции
    supports_sms = Column(Boolean, default=False)
    supports_voicemail = Column(Boolean, default=True)
    supports_recording = Column(Boolean, default=True)
    
    # Метаданные
    phone_metadata = Column(JSON, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    assigned_user = relationship("User", back_populates="phone_numbers")
    
    def __repr__(self):
        return f"<PhoneNumber(id={self.id}, e164='{self.e164}', user_id={self.assigned_user_id})>"

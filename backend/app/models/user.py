"""
Модель пользователя
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="sales_rep")  # admin, sales_rep, analyst
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="Europe/Berlin")
    language = Column(String(10), default="de")
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Настройки уведомлений
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    
    # Связи
    leads = relationship("Lead", back_populates="assigned_to_user")
    messages = relationship("Message", back_populates="created_by_user")
    calls = relationship("Call", back_populates="agent")
    phone_numbers = relationship("PhoneNumber", back_populates="assigned_user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

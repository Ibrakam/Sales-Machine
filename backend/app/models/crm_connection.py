"""
Модель CRM подключений
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class CRMConnection(Base):
    __tablename__ = "crm_connections"

    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(255), nullable=False)  # Название подключения
    crm_type = Column(String(50), nullable=False)  # hubspot, pipedrive, salesforce, ms_dynamics
    
    # Аутентификация
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    client_id = Column(String(255), nullable=True)
    client_secret = Column(String(255), nullable=True)
    
    # Организация
    org_id = Column(String(255), nullable=True)  # ID организации в CRM
    org_name = Column(String(255), nullable=True)
    
    # Настройки синхронизации
    is_active = Column(Boolean, default=True)
    sync_leads = Column(Boolean, default=True)
    sync_contacts = Column(Boolean, default=True)
    sync_deals = Column(Boolean, default=True)
    sync_companies = Column(Boolean, default=True)
    
    # Направление синхронизации
    sync_direction = Column(String(20), default="bidirectional")  # push, pull, bidirectional
    
    # Настройки полей
    field_mapping = Column(JSON, nullable=True)  # Маппинг полей между системами
    
    # Статистика
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    # Метаданные
    connection_metadata = Column(JSON, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<CRMConnection(id={self.id}, type='{self.crm_type}', org='{self.org_name}')>"

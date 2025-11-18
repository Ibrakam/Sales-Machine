"""
Модель прогнозов
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Период прогноза
    period_type = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Прогнозируемые значения
    predicted_revenue = Column(Float, nullable=False)
    predicted_deals = Column(Integer, nullable=False)
    predicted_leads = Column(Integer, nullable=False)
    
    # Точность прогноза
    accuracy_score = Column(Float, nullable=True)  # 0-1
    confidence_level = Column(Float, nullable=True)  # 0-1
    
    # Модель и параметры
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    model_parameters = Column(JSON, nullable=True)
    
    # Фактические значения (для оценки точности)
    actual_revenue = Column(Float, nullable=True)
    actual_deals = Column(Integer, nullable=True)
    actual_leads = Column(Integer, nullable=True)
    
    # Разбивка по менеджерам
    manager_breakdown = Column(JSON, nullable=True)  # {user_id: {revenue, deals, leads}}
    
    # Разбивка по продуктам/услугам
    product_breakdown = Column(JSON, nullable=True)
    
    # Метаданные
    notes = Column(String(1000), nullable=True)
    forecast_metadata = Column(JSON, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Forecast(id={self.id}, period='{self.period_start}' - '{self.period_end}', revenue={self.predicted_revenue})>"

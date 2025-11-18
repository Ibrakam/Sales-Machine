"""
Схемы для прогнозов
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ForecastBase(BaseModel):
    period_type: str = Field(..., min_length=1, max_length=20)
    period_start: datetime
    period_end: datetime
    predicted_revenue: float = Field(..., ge=0)
    predicted_deals: int = Field(..., ge=0)
    predicted_leads: int = Field(..., ge=0)


class ForecastCreate(ForecastBase):
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    model_parameters: Optional[Dict[str, Any]] = None
    manager_breakdown: Optional[Dict[str, Any]] = None
    product_breakdown: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ForecastUpdate(BaseModel):
    predicted_revenue: Optional[float] = Field(None, ge=0)
    predicted_deals: Optional[int] = Field(None, ge=0)
    predicted_leads: Optional[int] = Field(None, ge=0)
    accuracy_score: Optional[float] = Field(None, ge=0, le=1)
    confidence_level: Optional[float] = Field(None, ge=0, le=1)
    actual_revenue: Optional[float] = Field(None, ge=0)
    actual_deals: Optional[int] = Field(None, ge=0)
    actual_leads: Optional[int] = Field(None, ge=0)
    manager_breakdown: Optional[Dict[str, Any]] = None
    product_breakdown: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ForecastInDB(ForecastBase):
    id: int
    accuracy_score: Optional[float] = None
    confidence_level: Optional[float] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    model_parameters: Optional[Dict[str, Any]] = None
    actual_revenue: Optional[float] = None
    actual_deals: Optional[int] = None
    actual_leads: Optional[int] = None
    manager_breakdown: Optional[Dict[str, Any]] = None
    product_breakdown: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Forecast(ForecastInDB):
    pass


class ForecastList(BaseModel):
    """Список прогнозов"""
    items: list[Forecast]
    total: int

"""
API endpoints для прогнозов
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.models.forecast import Forecast
from app.schemas.forecast import Forecast as ForecastSchema, ForecastCreate, ForecastUpdate, ForecastList

router = APIRouter()


@router.get("/", response_model=ForecastList)
async def get_forecasts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка прогнозов"""
    forecasts = db.query(Forecast).all()
    return ForecastList(items=forecasts, total=len(forecasts))


@router.post("/", response_model=ForecastSchema)
async def create_forecast(
    forecast_create: ForecastCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание нового прогноза"""
    # Только аналитики и админы могут создавать прогнозы
    if current_user.role not in ["analyst", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    forecast_data = forecast_create.dict()
    forecast = Forecast(**forecast_data)
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    
    return forecast


@router.get("/{forecast_id}", response_model=ForecastSchema)
async def get_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение прогноза по ID"""
    forecast = db.query(Forecast).filter(Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )
    
    return forecast


@router.put("/{forecast_id}", response_model=ForecastSchema)
async def update_forecast(
    forecast_id: int,
    forecast_update: ForecastUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновление прогноза"""
    # Только аналитики и админы могут обновлять прогнозы
    if current_user.role not in ["analyst", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    forecast = db.query(Forecast).filter(Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )
    
    update_data = forecast_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(forecast, field, value)
    
    db.commit()
    db.refresh(forecast)
    
    return forecast


@router.delete("/{forecast_id}")
async def delete_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Удаление прогноза (только для админов)"""
    forecast = db.query(Forecast).filter(Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )
    
    db.delete(forecast)
    db.commit()
    
    return {"message": "Forecast deleted successfully"}


@router.post("/generate")
async def generate_forecast(
    period_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Генерация нового прогноза с помощью AI"""
    # Только аналитики и админы могут генерировать прогнозы
    if current_user.role not in ["analyst", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # TODO: Реализовать AI генерацию прогноза
    # Здесь будет вызов AI сервиса для создания прогноза
    
    return {"message": "Forecast generation initiated", "period_type": period_type}

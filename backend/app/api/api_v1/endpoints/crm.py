"""
API endpoints для CRM интеграций
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.models.crm_connection import CRMConnection
from app.schemas.crm_connection import CRMConnection as CRMConnectionSchema, CRMConnectionCreate, CRMConnectionUpdate, CRMConnectionList

router = APIRouter()


@router.get("/connections", response_model=CRMConnectionList)
async def get_crm_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Получение списка CRM подключений (только для админов)"""
    connections = db.query(CRMConnection).all()
    return CRMConnectionList(items=connections, total=len(connections))


@router.post("/connections", response_model=CRMConnectionSchema)
async def create_crm_connection(
    connection_create: CRMConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Создание нового CRM подключения (только для админов)"""
    connection_data = connection_create.dict()
    connection = CRMConnection(**connection_data)
    db.add(connection)
    db.commit()
    db.refresh(connection)
    
    return connection


@router.get("/connections/{connection_id}", response_model=CRMConnectionSchema)
async def get_crm_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Получение CRM подключения по ID (только для админов)"""
    connection = db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRM connection not found"
        )
    
    return connection


@router.put("/connections/{connection_id}", response_model=CRMConnectionSchema)
async def update_crm_connection(
    connection_id: int,
    connection_update: CRMConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Обновление CRM подключения (только для админов)"""
    connection = db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRM connection not found"
        )
    
    update_data = connection_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(connection, field, value)
    
    db.commit()
    db.refresh(connection)
    
    return connection


@router.delete("/connections/{connection_id}")
async def delete_crm_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Удаление CRM подключения (только для админов)"""
    connection = db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRM connection not found"
        )
    
    db.delete(connection)
    db.commit()
    
    return {"message": "CRM connection deleted successfully"}


@router.post("/connections/{connection_id}/sync")
async def sync_crm_data(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Синхронизация данных с CRM (только для админов)"""
    connection = db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRM connection not found"
        )
    
    if not connection.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CRM connection is not active"
        )
    
    # TODO: Реализовать синхронизацию с CRM
    # Здесь будет логика синхронизации данных
    
    return {"message": "CRM sync initiated", "connection_id": connection_id}


@router.get("/connections/{connection_id}/status")
async def get_crm_connection_status(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Получение статуса CRM подключения (только для админов)"""
    connection = db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRM connection not found"
        )
    
    # TODO: Реализовать проверку статуса подключения
    # Здесь будет логика проверки доступности CRM API
    
    return {
        "connection_id": connection_id,
        "is_active": connection.is_active,
        "last_sync": connection.last_sync_at,
        "sync_count": connection.sync_count,
        "error_count": connection.error_count,
        "last_error": connection.last_error
    }

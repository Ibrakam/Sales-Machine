"""
API endpoints для сообщений
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.message import Message
from app.schemas.message import Message as MessageSchema, MessageCreate, MessageUpdate, MessageList

router = APIRouter()


@router.get("/", response_model=MessageList)
async def get_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    lead_id: Optional[int] = Query(None),
    message_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка сообщений с фильтрацией"""
    query = db.query(Message)
    
    # Фильтрация по лиду
    if lead_id:
        query = query.filter(Message.lead_id == lead_id)
    
    # Фильтрация по типу сообщения
    if message_type:
        query = query.filter(Message.message_type == message_type)
    
    # Фильтрация по статусу
    if status:
        query = query.filter(Message.status == status)
    
    # Фильтрация по создателю (если не админ)
    if current_user.role != "admin":
        query = query.filter(Message.created_by == current_user.id)
    
    # Подсчет общего количества
    total = query.count()
    
    # Пагинация
    messages = query.offset(skip).limit(limit).all()
    
    return MessageList(
        items=messages,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=MessageSchema)
async def create_message(
    message_create: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание нового сообщения"""
    message_data = message_create.dict()
    message_data["created_by"] = current_user.id
    
    message = Message(**message_data)
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message


@router.get("/{message_id}", response_model=MessageSchema)
async def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение сообщения по ID"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and message.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return message


@router.put("/{message_id}", response_model=MessageSchema)
async def update_message(
    message_id: int,
    message_update: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновление сообщения"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and message.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Обновляем данные
    update_data = message_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(message, field, value)
    
    db.commit()
    db.refresh(message)
    
    return message


@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удаление сообщения"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and message.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(message)
    db.commit()
    
    return {"message": "Message deleted successfully"}


@router.post("/{message_id}/send")
async def send_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Отправка сообщения"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and message.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # TODO: Реализовать отправку сообщения
    # Здесь будет логика отправки через соответствующий канал
    
    return {"message": "Message sent successfully", "message_id": message_id}

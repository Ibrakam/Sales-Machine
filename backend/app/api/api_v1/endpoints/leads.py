"""
API endpoints для лидов
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.lead import Lead
from app.models.lead_interaction import LeadInteraction, InteractionAuthor as ModelInteractionAuthor
from app.models.user import User
from app.schemas.lead import Lead as LeadSchema, LeadCreate, LeadList, LeadUpdate
from app.schemas.lead_interaction import (
    InteractionAuthor,
    LeadInteraction as LeadInteractionSchema,
    LeadInteractionCreate,
)

router = APIRouter()


@router.get("/", response_model=LeadList)
async def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    score_category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка лидов с фильтрацией"""
    query = db.query(Lead)
    
    # Фильтрация по назначенному пользователю
    if current_user.role != "admin":
        query = query.filter(Lead.assigned_to == current_user.id)
    elif assigned_to:
        query = query.filter(Lead.assigned_to == assigned_to)
    
    # Поиск по тексту
    if search:
        search_filter = or_(
            Lead.name.ilike(f"%{search}%"),
            Lead.company.ilike(f"%{search}%"),
            Lead.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Фильтрация по статусу
    if status:
        query = query.filter(Lead.status == status)
    
    # Фильтрация по категории скоринга
    if score_category:
        query = query.filter(Lead.score_category == score_category)
    
    # Подсчет общего количества
    total = query.count()
    
    # Пагинация
    leads = query.offset(skip).limit(limit).all()
    
    return LeadList(
        items=leads,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=LeadSchema)
async def create_lead(
    lead_create: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание нового лида"""
    # Проверяем, что email уникален (если указан)
    if lead_create.email:
        existing_lead = db.query(Lead).filter(Lead.email == lead_create.email).first()
        if existing_lead:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lead with this email already exists"
            )
    
    # Создаем лида
    lead_data = lead_create.dict()
    if not lead_data.get("company"):
        lead_data["company"] = "Новый клиент"
    lead = Lead(**lead_data)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return lead


@router.get("/{lead_id}", response_model=LeadSchema)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение лида по ID"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and lead.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return lead


@router.put("/{lead_id}", response_model=LeadSchema)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновление лида"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and lead.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Обновляем данные
    update_data = lead_update.dict(exclude_unset=True)
    
    if "company" in update_data and (update_data["company"] is None or update_data["company"] == ""):
        update_data["company"] = lead.company or "Новый клиент"

    for field, value in update_data.items():
        setattr(lead, field, value)
    
    db.commit()
    db.refresh(lead)
    
    return lead


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Удаление лида (только для админов)"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    db.delete(lead)
    db.commit()
    
    return {"message": "Lead deleted successfully"}


@router.get("/{lead_id}/interactions", response_model=List[LeadInteractionSchema])
async def get_lead_interactions(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение истории взаимодействий с лидом"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    if current_user.role != "admin" and lead.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    interactions = (
        db.query(LeadInteraction)
        .filter(LeadInteraction.lead_id == lead_id)
        .order_by(LeadInteraction.created_at.asc())
        .all()
    )
    return interactions


@router.post("/{lead_id}/interactions", response_model=LeadInteractionSchema, status_code=status.HTTP_201_CREATED)
async def create_lead_interaction(
    lead_id: int,
    interaction_data: LeadInteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Добавление заметки/диалога по лиду"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    if current_user.role != "admin" and lead.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Используем enum из модели для SQLAlchemy (конвертируем из схемы если нужно)
    if interaction_data.author_type:
        # Конвертируем enum из схемы в enum модели
        author_type = ModelInteractionAuthor(interaction_data.author_type.value)
    else:
        author_type = ModelInteractionAuthor.ADMIN
    author_name = interaction_data.author_name or current_user.full_name or current_user.email

    interaction = LeadInteraction(
        lead_id=lead_id,
        author_type=author_type,  # Используем enum объект напрямую
        author_name=author_name,
        message=interaction_data.message,
        context=interaction_data.context,
    )

    lead.last_contacted = datetime.utcnow()

    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    db.refresh(lead)

    return interaction


@router.post("/{lead_id}/score")
async def score_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """AI-скоринг лида"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and lead.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # TODO: Реализовать AI-скоринг
    # Здесь будет вызов AI сервиса для оценки лида
    
    return {"message": "Lead scoring initiated", "lead_id": lead_id}

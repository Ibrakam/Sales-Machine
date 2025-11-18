"""
API endpoints для звонков
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.call import Call, CallTranscript, CallTask
from app.schemas.call import Call as CallSchema, CallCreate, CallUpdate, CallList, CallTranscript as CallTranscriptSchema, CallTask as CallTaskSchema

router = APIRouter()


@router.get("/", response_model=CallList)
async def get_calls(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    lead_id: Optional[int] = Query(None),
    direction: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка звонков с фильтрацией"""
    query = db.query(Call)
    
    # Фильтрация по агенту (если не админ)
    if current_user.role != "admin":
        query = query.filter(Call.agent_id == current_user.id)
    
    # Фильтрация по лиду
    if lead_id:
        query = query.filter(Call.lead_id == lead_id)
    
    # Фильтрация по направлению
    if direction:
        query = query.filter(Call.direction == direction)
    
    # Фильтрация по статусу
    if status:
        query = query.filter(Call.status == status)
    
    # Подсчет общего количества
    total = query.count()
    
    # Пагинация
    calls = query.offset(skip).limit(limit).all()
    
    return CallList(
        items=calls,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=CallSchema)
async def create_call(
    call_create: CallCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание нового звонка"""
    call_data = call_create.dict()
    call_data["agent_id"] = current_user.id
    
    call = Call(**call_data)
    db.add(call)
    db.commit()
    db.refresh(call)
    
    return call


@router.get("/{call_id}", response_model=CallSchema)
async def get_call(
    call_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение звонка по ID"""
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and call.agent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return call


@router.put("/{call_id}", response_model=CallSchema)
async def update_call(
    call_id: int,
    call_update: CallUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновление звонка"""
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and call.agent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_data = call_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(call, field, value)
    
    db.commit()
    db.refresh(call)
    
    return call


@router.get("/{call_id}/transcript", response_model=CallTranscriptSchema)
async def get_call_transcript(
    call_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение транскрипта звонка"""
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and call.agent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    transcript = db.query(CallTranscript).filter(CallTranscript.call_id == call_id).first()
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call transcript not found"
        )
    
    return transcript


@router.post("/{call_id}/transcript")
async def create_call_transcript(
    call_id: int,
    transcript_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание транскрипта звонка"""
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and call.agent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # TODO: Реализовать создание транскрипта
    # Здесь будет логика обработки аудио и создания транскрипта
    
    return {"message": "Call transcript creation initiated", "call_id": call_id}


@router.get("/tasks", response_model=List[CallTaskSchema])
async def get_call_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка задач по звонкам"""
    query = db.query(CallTask)
    
    # Фильтрация по назначенному пользователю
    if current_user.role != "admin":
        query = query.filter(CallTask.assigned_to == current_user.id)
    
    tasks = query.all()
    return tasks


@router.post("/tasks", response_model=CallTaskSchema)
async def create_call_task(
    task_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание задачи по звонку"""
    task_data["created_by"] = current_user.id
    
    task = CallTask(**task_data)
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task

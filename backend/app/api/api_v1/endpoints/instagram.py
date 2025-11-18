"""
Instagram integration endpoints
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.instagram_account import InstagramAccount
from app.models.lead import Lead
from app.schemas.instagram import (
    InstagramAccount as InstagramAccountSchema,
    InstagramAccountCreate,
    InstagramAccountUpdate,
    InstagramSyncResponse,
)
from app.schemas.lead import LeadSource, LeadStatus
from app.models.user import User

router = APIRouter()


def _get_account(db: Session) -> Optional[InstagramAccount]:
    return db.query(InstagramAccount).first()


@router.get("/account", response_model=Optional[InstagramAccountSchema])
async def get_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Возвращает подключенный Instagram аккаунт (если есть)"""
    return _get_account(db)


@router.post("/account", response_model=InstagramAccountSchema, status_code=status.HTTP_200_OK)
async def upsert_account(
    account_data: InstagramAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Создание или обновление подключения Instagram"""
    account = _get_account(db)
    now = datetime.utcnow()
    payload = account_data.dict(exclude_unset=True)

    status_value = "connected" if payload.get("access_token") else "pending"

    if account:
        for field, value in payload.items():
            setattr(account, field, value)
        account.status = status_value or account.status
        if account.status == "connected":
            account.connected_at = now
        account.updated_at = now
    else:
        account = InstagramAccount(
            **payload,
            status=status_value,
            connected_at=now if status_value == "connected" else None,
            updated_at=now,
        )
        db.add(account)

    db.commit()
    db.refresh(account)
    return account


@router.put("/account", response_model=InstagramAccountSchema)
async def update_account(
    account_update: InstagramAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Частичное обновление данных Instagram аккаунта"""
    account = _get_account(db)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instagram account not configured",
        )

    payload = account_update.dict(exclude_unset=True)
    now = datetime.utcnow()

    for field, value in payload.items():
        setattr(account, field, value)

    if payload.get("status") == "connected" and not account.connected_at:
        account.connected_at = now

    account.updated_at = now
    db.commit()
    db.refresh(account)
    return account


@router.post("/sync", response_model=InstagramSyncResponse)
async def sync_instagram_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Имитация импорта лидов из Instagram DM"""
    account = _get_account(db)
    if not account or account.status != "connected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instagram account is not connected",
        )

    now = datetime.utcnow()
    sample_leads = [
        {
            "name": "Ирина Сергеева",
            "email": "irina.sergeeva@example.com",
            "phone": "+7 (916) 123-45-67",
            "notes": "Запрос в Instagram: нужен корпоративный сайт для IT-компании.",
            "custom_fields": {"requested_service": "Корпоративный сайт", "budget": "≈ 6 000 €"},
            "tags": ["instagram", "web", "it-services"],
        },
        {
            "name": "DigitalFlow Studio",
            "email": "ceo@digitalflow.studio",
            "phone": "+49 151 23456789",
            "company": "DigitalFlow Studio",
            "notes": "Хочет обсудить SEO и техническую поддержку корпоративного портала.",
            "custom_fields": {"requested_service": "SEO + поддержка", "preferred_language": "de"},
            "tags": ["instagram", "seo"],
        },
        {
            "name": "Артем Ковалев",
            "email": "artem.kovalev@example.com",
            "phone": "+7 (903) 555-12-90",
            "notes": "Написал в Direct: требуются услуги интеграции CRM и разработка чат-бота.",
            "custom_fields": {"requested_service": "CRM + чат-бот", "priority": "high"},
            "tags": ["instagram", "automation"],
        },
    ]

    created_leads: List[Lead] = []

    for item in sample_leads:
        # Проверяем дубликаты по email
        email = item.get("email")
        if email:
            duplicate = db.query(Lead).filter(Lead.email == email).first()
            if duplicate:
                continue

        lead = Lead(
            name=item["name"],
            email=email,
            phone=item.get("phone"),
            company=item.get("company"),
            status=LeadStatus.NEW.value,
            source=LeadSource.SOCIAL.value,
            source_data={
                "platform": "instagram",
                "username": account.username,
                "synced_at": now.isoformat(),
            },
            tags=item.get("tags"),
            custom_fields=item.get("custom_fields"),
            notes=item.get("notes"),
        )
        db.add(lead)
        created_leads.append(lead)

    if not created_leads:
        return InstagramSyncResponse(synced=0, created_leads=[])

    account.last_sync_at = now
    integration_metadata = account.integration_metadata or {}
    integration_metadata["sync_count"] = integration_metadata.get("sync_count", 0) + 1
    account.integration_metadata = integration_metadata
    account.updated_at = now

    db.commit()

    for lead in created_leads:
        db.refresh(lead)

    return InstagramSyncResponse(
        synced=len(created_leads),
        created_leads=created_leads,
    )

"""
API endpoints для AI функций
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.lead import Lead
from app.models.lead_interaction import LeadInteraction, InteractionAuthor
from app.models.user import User
from app.services.ai_chat import AIChatServiceError, generate_sales_assistant_reply

router = APIRouter()


class EmailGenerationRequest(BaseModel):
    lead_id: int
    template_type: str = "cold_outreach"
    language: str = "de"
    tone: str = "professional"
    custom_prompt: Optional[str] = None


class EmailGenerationResponse(BaseModel):
    subject: str
    body: str
    alternative_subject: Optional[str] = None
    alternative_body: Optional[str] = None
    tokens_used: int
    model_used: str


class LeadScoringRequest(BaseModel):
    lead_id: int
    force_rescore: bool = False


class LeadScoringResponse(BaseModel):
    lead_id: int
    score: float
    score_category: str
    reasoning: str
    factors: Dict[str, Any]


class ChatHistoryMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    lead_id: Optional[int] = None
    history: Optional[List[ChatHistoryMessage]] = None


class ChatResponse(BaseModel):
    reply: str
    lead_id: Optional[int] = None
    usage: Optional[Dict[str, Optional[int]]] = None
    model: Optional[str] = None


@router.post("/generate-email", response_model=EmailGenerationResponse)
async def generate_email(
    request: EmailGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Генерация персонализированного email для лида"""
    # TODO: Реализовать AI генерацию email
    # Здесь будет вызов OpenAI API для создания персонализированного письма
    
    return EmailGenerationResponse(
        subject="Test Subject",
        body="Test email body",
        tokens_used=150,
        model_used="gpt-4"
    )


@router.post("/score-lead", response_model=LeadScoringResponse)
async def score_lead(
    request: LeadScoringRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """AI-скоринг лида"""
    # TODO: Реализовать AI скоринг лида
    # Здесь будет анализ лида и присвоение скора
    
    return LeadScoringResponse(
        lead_id=request.lead_id,
        score=75.5,
        score_category="warm",
        reasoning="High company revenue and active on LinkedIn",
        factors={
            "company_size": "large",
            "industry": "technology",
            "engagement": "high"
        }
    )


@router.post("/analyze-call")
async def analyze_call(
    call_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """AI-анализ звонка"""
    # TODO: Реализовать AI анализ звонка
    # Здесь будет анализ транскрипта звонка
    
    return {"message": "Call analysis initiated", "call_id": call_id}


@router.post("/generate-forecast")
async def generate_forecast(
    period_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """AI-генерация прогноза продаж"""
    # Только аналитики и админы могут генерировать прогнозы
    if current_user.role not in ["analyst", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # TODO: Реализовать AI генерацию прогноза
    # Здесь будет анализ исторических данных и создание прогноза
    
    return {"message": "Forecast generation initiated", "period_type": period_type}


@router.get("/models")
async def get_available_models():
    """Получение списка доступных AI моделей"""
    return {
        "models": [
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "type": "text",
                "max_tokens": 8192,
                "cost_per_1k_tokens": 0.03
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "type": "text",
                "max_tokens": 128000,
                "cost_per_1k_tokens": 0.01
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "type": "text",
                "max_tokens": 4096,
                "cost_per_1k_tokens": 0.002
            }
        ]
    }


@router.get("/usage")
async def get_ai_usage(
    current_user: User = Depends(get_current_active_user)
):
    """Получение статистики использования AI"""
    # TODO: Реализовать подсчет использования AI
    # Здесь будет статистика по токенам, запросам и т.д.
    
    return {
        "user_id": current_user.id,
        "tokens_used_today": 1500,
        "tokens_used_month": 45000,
        "requests_today": 25,
        "requests_month": 750,
        "cost_today": 0.45,
        "cost_month": 13.50
    }
@router.post("/chat", response_model=ChatResponse)
async def chat_with_sales_agent(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Чат с AI-агентом внутри админ-панели"""
    system_messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "Ты — виртуальный менеджер по продажам IT-услуг. "
                "Компания продает разработку веб-проектов, интеграцию CRM, автоматизацию "
                "бизнес-процессов и поддержку инфраструктуры. "
                "Отвечай профессионально, по существу, предлагай следующие шаги и уточняющие вопросы."
            ),
        }
    ]

    lead: Optional[Lead] = None
    if chat_request.lead_id is not None:
        lead = db.query(Lead).filter(Lead.id == chat_request.lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found",
            )
        if current_user.role != "admin" and lead.assigned_to not in (None, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

        lead_context = (
            "Контекст клиента:\n"
            f"Имя: {lead.name}\n"
            f"Email: {lead.email or 'не указан'}\n"
            f"Телефон: {lead.phone or 'не указан'}\n"
            f"Статус: {lead.status}\n"
            f"Источник: {lead.source or 'не указан'}\n"
            f"Заметки: {lead.notes or '—'}"
        )
        system_messages.append({"role": "system", "content": lead_context})

        recent_interactions = (
            db.query(LeadInteraction)
            .filter(LeadInteraction.lead_id == lead.id)
            .order_by(LeadInteraction.created_at.desc())
            .limit(5)
            .all()
        )
        if recent_interactions:
            formatted_history = "\n".join(
                f"{interaction.created_at.strftime('%Y-%m-%d %H:%M')}: "
                f"{interaction.author_type.value} — {interaction.message}"
                for interaction in reversed(recent_interactions)
            )
            system_messages.append(
                {
                    "role": "system",
                    "content": f"Последние взаимодействия с клиентом:\n{formatted_history}",
                }
            )

    if chat_request.history:
        for entry in chat_request.history:
            system_messages.append({"role": entry.role, "content": entry.content})

    system_messages.append({"role": "user", "content": chat_request.message})

    try:
        ai_result = generate_sales_assistant_reply(system_messages)
    except AIChatServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    reply_text = ai_result.get("content") or "Извините, сейчас я не могу ответить."

    if lead:
        author_name = current_user.full_name or current_user.email or "Администратор"
        db.add(
            LeadInteraction(
                lead_id=lead.id,
                author_type=InteractionAuthor.ADMIN,
                author_name=author_name,
                message=chat_request.message,
            )
        )
        db.add(
            LeadInteraction(
                lead_id=lead.id,
                author_type=InteractionAuthor.AI,
                author_name="AI Sales Assistant",
                message=reply_text,
            )
        )
        lead.last_contacted = datetime.utcnow()
        db.commit()

    return ChatResponse(
        reply=reply_text,
        lead_id=chat_request.lead_id,
        usage=ai_result.get("usage"),
        model=ai_result.get("model"),
    )

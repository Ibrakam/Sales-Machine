"""
Сервис для общения с OpenAI ChatGPT
"""
from functools import lru_cache
from typing import Dict, List

from loguru import logger
from openai import OpenAI

from app.core.config import settings


class AIChatServiceError(Exception):
    """Исключение при ошибке общения с AI"""


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    if not settings.OPENAI_API_KEY:
        raise AIChatServiceError("OpenAI API key is not configured")
    return OpenAI(api_key="")


def generate_sales_assistant_reply(
    messages: List[Dict[str, str]],
    *,
    temperature: float = 0.3,
    max_tokens: int | None = None,
) -> Dict[str, object]:
    """Отправка запроса в OpenAI и получение ответа"""
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or settings.OPENAI_MAX_TOKENS,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("OpenAI chat request failed")
        raise AIChatServiceError("Не удалось получить ответ от AI") from exc

    choice = response.choices[0]
    usage = getattr(response, "usage", None)

    return {
        "content": choice.message.content.strip() if choice.message and choice.message.content else "",
        "model": response.model,
        "usage": {
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }
        if usage
        else None,
    }

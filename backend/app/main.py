"""
AI Sales Assistant - FastAPI приложение
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import os
import time

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.database import engine
from app.models import Base
from app.utils.bootstrap import seed_demo_users




app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SaaS-платформа для автоматизации процесса продаж в B2B-сегменте",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("startup")
async def on_startup():
    """Создание таблиц при старте приложения (опционально)"""
    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)
        seed_demo_users()

# CORS middleware
cors_origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",")]
# Для тестирования с ngrok/cloudflared разрешаем все источники (только для разработки!)
allow_all_origins = (
    any("ngrok" in origin for origin in cors_origins) or 
    any("trycloudflare" in origin for origin in cors_origins) or
    os.getenv("ALLOW_ALL_ORIGINS", "false").lower() == "true"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if not allow_all_origins else ["*"],
    allow_credentials=not allow_all_origins,  # Нельзя использовать credentials с allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Trusted hosts middleware (отключено для локальной разработки)
# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=["*"]
#     )

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

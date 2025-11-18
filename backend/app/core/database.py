"""
Конфигурация базы данных
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis

from app.core.config import settings

# Настройки подключения к БД
database_url = settings.DATABASE_URL

# Базовая конфигурация
engine_kwargs = {
    "echo": settings.LOG_LEVEL == "DEBUG",
}

if database_url.startswith("sqlite"):
    # SQLite настройки
    db_path = database_url.replace("sqlite:///", "")
    if db_path not in (":memory:", ""):
        # Создаем директорию для файла БД, если нужно
        db_file = Path(db_path).expanduser().resolve()
        db_file.parent.mkdir(parents=True, exist_ok=True)
        database_url = f"sqlite:///{db_file.as_posix()}"
    
    # SQLite специфичные настройки
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    
    # Для in-memory БД используем StaticPool
    if db_path in (":memory:", ""):
        engine_kwargs["poolclass"] = StaticPool
else:
    # PostgreSQL и другие БД
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(database_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Redis (опционально)
redis_client = None
if settings.REDIS_URL:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        # Проверка подключения
        redis_client.ping()
    except (redis.ConnectionError, redis.TimeoutError, ValueError):
        redis_client = None
        import warnings
        warnings.warn("Redis не доступен, некоторые функции могут не работать", UserWarning)


def get_db():
    """Dependency для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    """Dependency для получения Redis клиента (может быть None если Redis не доступен)"""
    if redis_client is None:
        raise RuntimeError("Redis не настроен. Установите REDIS_URL в настройках или запустите Redis.")
    return redis_client

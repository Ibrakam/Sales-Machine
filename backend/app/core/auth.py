"""
Простая система аутентификации для демонстрации
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import hashlib
from app.core.config import settings

# Демо-пользователи (в реальной системе будут в БД)
DEMO_USERS = {
    "admin@example.com": {
        "id": 1,
        "email": "admin@example.com",
        "password": "password",  # В реальной системе будет хеш
        "role": "admin",
        "name": "Администратор",
        "is_active": True,
        "created_at": datetime.utcnow()
    },
    "sales@example.com": {
        "id": 2,
        "email": "sales@example.com", 
        "password": "sales123",
        "role": "sales_rep",
        "name": "Менеджер по продажам",
        "is_active": True,
        "created_at": datetime.utcnow()
    },
    "analyst@example.com": {
        "id": 3,
        "email": "analyst@example.com",
        "password": "analyst123",
        "role": "analyst", 
        "name": "Аналитик",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
}

def verify_password(plain_password: str, stored_password: str) -> bool:
    """Проверка пароля (упрощенная для демо)"""
    return plain_password == stored_password

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Аутентификация пользователя"""
    user = DEMO_USERS.get(email)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Создание refresh токена"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Проверка JWT токена"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Получение пользователя по ID"""
    for user in DEMO_USERS.values():
        if user["id"] == user_id:
            return user
    return None

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Получение пользователя по email"""
    return DEMO_USERS.get(email)

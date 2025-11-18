"""
Вспомогательные функции для инициализации данных
"""
from sqlalchemy.orm import Session

from app.core.auth import DEMO_USERS
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def seed_demo_users() -> None:
    """Создает демо-пользователей в БД, если они отсутствуют"""
    db: Session = SessionLocal()
    try:
        for demo_user in DEMO_USERS.values():
            user = db.query(User).filter(User.id == demo_user["id"]).first()
            if user:
                continue

            username = demo_user["email"].split("@")[0]
            hashed_password = get_password_hash(demo_user["password"])

            user = User(
                id=demo_user["id"],
                email=demo_user["email"],
                username=username,
                full_name=demo_user.get("name"),
                hashed_password=hashed_password,
                role=demo_user.get("role", "sales_rep"),
                is_active=demo_user.get("is_active", True),
                is_verified=True,
            )
            db.add(user)

        db.commit()
    finally:
        db.close()

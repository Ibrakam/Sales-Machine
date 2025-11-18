# Руководство разработчика

## Структура проекта

```
ai_agent/
├── backend/                 # FastAPI приложение
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   └── api_v1/
│   │   │       ├── api.py  # Главный роутер
│   │   │       └── endpoints/  # Отдельные endpoints
│   │   ├── core/           # Конфигурация, безопасность
│   │   │   ├── config.py   # Настройки приложения
│   │   │   ├── database.py # Подключение к БД
│   │   │   └── security.py # JWT, хеширование паролей
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── services/       # Бизнес-логика
│   │   └── utils/          # Утилиты
│   ├── tests/              # Тесты
│   ├── alembic/            # Миграции БД
│   └── requirements.txt
├── frontend/               # Next.js приложение
│   ├── src/
│   │   ├── app/            # App Router
│   │   ├── components/     # React компоненты
│   │   │   └── ui/         # Базовые UI компоненты
│   │   ├── lib/            # Утилиты и конфигурация
│   │   ├── hooks/          # React хуки
│   │   └── types/          # TypeScript типы
│   └── package.json
├── docker/                 # Docker конфигурации
├── docs/                   # Документация
└── docker-compose.yml      # Локальная разработка
```

## Backend разработка

### Настройка окружения

1. **Создание виртуального окружения**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

2. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

3. **Настройка переменных окружения**
```bash
cp env.example .env
# Отредактируйте .env файл
```

4. **Запуск в режиме разработки**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Создание новых API endpoints

1. **Создание схемы (Pydantic)**
```python
# app/schemas/new_feature.py
from pydantic import BaseModel
from typing import Optional

class NewFeatureCreate(BaseModel):
    name: str
    description: Optional[str] = None

class NewFeatureUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class NewFeature(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
```

2. **Создание модели (SQLAlchemy)**
```python
# app/models/new_feature.py
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class NewFeature(Base):
    __tablename__ = "new_features"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

3. **Создание endpoint**
```python
# app/api/api_v1/endpoints/new_feature.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.new_feature import NewFeature, NewFeatureCreate, NewFeatureUpdate

router = APIRouter()

@router.get("/", response_model=List[NewFeature])
async def get_new_features(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка новых функций"""
    features = db.query(NewFeature).offset(skip).limit(limit).all()
    return features

@router.post("/", response_model=NewFeature)
async def create_new_feature(
    feature_create: NewFeatureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание новой функции"""
    feature = NewFeature(**feature_create.dict())
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature
```

4. **Добавление в главный роутер**
```python
# app/api/api_v1/api.py
from app.api.api_v1.endpoints import new_feature

api_router.include_router(new_feature.router, prefix="/new-features", tags=["new-features"])
```

### Миграции базы данных

1. **Создание миграции**
```bash
cd backend
alembic revision --autogenerate -m "Add new feature table"
```

2. **Применение миграции**
```bash
alembic upgrade head
```

3. **Откат миграции**
```bash
alembic downgrade -1
```

### Тестирование

1. **Запуск тестов**
```bash
pytest
```

2. **Запуск с покрытием**
```bash
pytest --cov=app tests/
```

3. **Пример теста**
```python
# tests/test_new_feature.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_new_feature():
    response = client.post(
        "/api/v1/new-features/",
        json={"name": "Test Feature", "description": "Test Description"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Feature"
```

## Frontend разработка

### Настройка окружения

1. **Установка зависимостей**
```bash
cd frontend
npm install
```

2. **Настройка переменных окружения**
```bash
cp env.example .env.local
# Отредактируйте .env.local файл
```

3. **Запуск в режиме разработки**
```bash
npm run dev
```

### Создание новых компонентов

1. **Создание страницы**
```tsx
// src/app/new-page/page.tsx
'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function NewPage() {
  return (
    <div className="container mx-auto py-6">
      <Card>
        <CardHeader>
          <CardTitle>Новая страница</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Содержимое страницы</p>
        </CardContent>
      </Card>
    </div>
  )
}
```

2. **Создание компонента**
```tsx
// src/components/NewComponent.tsx
import { Button } from '@/components/ui/button'

interface NewComponentProps {
  title: string
  onAction: () => void
}

export function NewComponent({ title, onAction }: NewComponentProps) {
  return (
    <div className="p-4 border rounded-lg">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <Button onClick={onAction}>Действие</Button>
    </div>
  )
}
```

3. **Создание хука**
```tsx
// src/hooks/useNewFeature.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'

export function useNewFeatures() {
  return useQuery({
    queryKey: ['new-features'],
    queryFn: () => api.get('/new-features/').then(res => res.data),
  })
}

export function useCreateNewFeature() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: any) => api.post('/new-features/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['new-features'] })
    },
  })
}
```

### Стилизация

Проект использует Tailwind CSS с shadcn/ui компонентами:

1. **Добавление новых стилей**
```tsx
// Используйте Tailwind классы
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  <h2 className="text-xl font-bold text-gray-900">Заголовок</h2>
  <Button variant="outline">Кнопка</Button>
</div>
```

2. **Создание кастомных компонентов**
```tsx
// src/components/ui/custom-component.tsx
import { cn } from '@/lib/utils'

interface CustomComponentProps {
  className?: string
  children: React.ReactNode
}

export function CustomComponent({ className, children }: CustomComponentProps) {
  return (
    <div className={cn("custom-styles", className)}>
      {children}
    </div>
  )
}
```

## Работа с Git

### Git Flow

1. **Создание feature ветки**
```bash
git checkout -b feature/new-feature
```

2. **Коммиты**
```bash
git add .
git commit -m "feat: add new feature"
```

3. **Push и создание PR**
```bash
git push origin feature/new-feature
# Создать Pull Request в GitHub
```

### Конвенции коммитов

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - новая функция
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг
- `test:` - добавление тестов
- `chore:` - обновление зависимостей

Примеры:
```bash
git commit -m "feat: add user authentication"
git commit -m "fix: resolve login validation issue"
git commit -m "docs: update API documentation"
```

## Отладка

### Backend

1. **Логирование**
```python
from loguru import logger

logger.info("User logged in", user_id=user.id)
logger.error("Database connection failed", error=str(e))
```

2. **Отладка в IDE**
- Установите breakpoints в коде
- Запустите в debug режиме
- Используйте `pdb` для отладки

### Frontend

1. **React DevTools**
- Установите расширение для браузера
- Используйте для отладки состояния компонентов

2. **Network tab**
- Проверяйте API запросы в DevTools
- Анализируйте ошибки и ответы

3. **Console logging**
```tsx
console.log('Debug info:', data)
console.error('Error:', error)
```

## Производительность

### Backend оптимизация

1. **Индексы базы данных**
```python
# Добавьте индексы для часто используемых полей
class Lead(Base):
    __tablename__ = "leads"
    
    email = Column(String(255), index=True)  # Индекс для поиска
    company = Column(String(255), index=True)
```

2. **Кэширование**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param):
    # Дорогие вычисления
    return result
```

3. **Асинхронные операции**
```python
import asyncio

async def process_multiple_items(items):
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results
```

### Frontend оптимизация

1. **Lazy loading**
```tsx
import { lazy, Suspense } from 'react'

const HeavyComponent = lazy(() => import('./HeavyComponent'))

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  )
}
```

2. **Мемоизация**
```tsx
import { memo, useMemo } from 'react'

const ExpensiveComponent = memo(({ data }) => {
  const processedData = useMemo(() => {
    return expensiveProcessing(data)
  }, [data])
  
  return <div>{processedData}</div>
})
```

3. **Виртуализация списков**
```tsx
import { FixedSizeList as List } from 'react-window'

function VirtualizedList({ items }) {
  return (
    <List
      height={600}
      itemCount={items.length}
      itemSize={50}
      itemData={items}
    >
      {({ index, style, data }) => (
        <div style={style}>
          {data[index].name}
        </div>
      )}
    </List>
  )
}
```

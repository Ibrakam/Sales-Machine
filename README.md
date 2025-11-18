# AI Sales Assistant

SaaS-платформа для автоматизации процесса продаж в B2B-сегменте с использованием искусственного интеллекта.

## 🚀 Функционал

- **Поиск и оценка лидов** - автоматический поиск и AI-скоринг потенциальных клиентов
- **Генерация писем** - персонализированные email-кампании на немецком/английском языках
- **Прогноз продаж** - предиктивная аналитика и прогнозирование выручки
- **CRM интеграции** - синхронизация с HubSpot, Pipedrive, Salesforce, MS Dynamics
- **Телефония** - WebRTC звонки, запись, транскрибация, AI-аналитика
- **Omnichannel** - единый инбокс для LinkedIn, WhatsApp, Email и других каналов

## 🛠 Технологический стек

### Backend

- **Python 3.11+** с FastAPI
- **PostgreSQL** + Redis
- **SQLAlchemy** ORM
- **Celery** для фоновых задач
- **OpenAI GPT-4** / Llama 3

### Frontend

- **React 18** с Next.js 14
- **TypeScript**
- **Tailwind CSS** + shadcn/ui
- **React Query** для управления состоянием

### DevOps

- **Docker** + docker-compose
- **GitHub Actions** CI/CD
- **AWS Frankfurt** / Hetzner
- **Prometheus** + Grafana

## 📁 Структура проекта

```
ai_agent/
├── backend/                 # FastAPI приложение
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Конфигурация, безопасность
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
│   │   ├── lib/            # Утилиты и конфигурация
│   │   └── types/          # TypeScript типы
│   └── package.json
├── docker/                 # Docker конфигурации
├── docs/                   # Документация
└── docker-compose.yml      # Локальная разработка
```

## 🚀 Быстрый старт

### Предварительные требования

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd ai_agent
```

### 2. Настройка переменных окружения

```bash
# Backend
cp backend/.env.example backend/.env
# Отредактируйте backend/.env с вашими настройками

# Frontend  
cp frontend/.env.example frontend/.env.local
# Отредактируйте frontend/.env.local
```

### 3. Запуск в режиме разработки

```bash
# Запуск всех сервисов
docker-compose up -d

# Или запуск отдельных сервисов
docker-compose up -d postgres redis
cd backend && python -m uvicorn app.main:app --reload
cd frontend && npm run dev
```

### 4. Доступ к приложению

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Adminer** (БД): http://localhost:8080

## 🔧 Конфигурация

### Backend (.env)

```env
# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/ai_sales_db
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4

# CRM интеграции
HUBSPOT_API_KEY=your-hubspot-key
PIPEDRIVE_API_KEY=your-pipedrive-key

# Телефония
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AI Sales Assistant
```

## 📊 Роли пользователей

- **Admin** - полный доступ ко всем функциям
- **Sales Rep** - работа с лидами, звонки, письма
- **Analyst** - аналитика и отчеты

## 🔐 Безопасность

- JWT токены с refresh механизмом
- Роли и права доступа
- GDPR соответствие
- Шифрование чувствительных данных
- Rate limiting

## 📈 Мониторинг

- Логирование через loguru
- Метрики Prometheus
- Health checks
- Error tracking

## 🧪 Тестирование

```bash
# Backend тесты
cd backend
pytest --cov=app tests/

# Frontend тесты
cd frontend
npm test
```

## 📚 API Документация

После запуска backend доступна по адресу:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🚀 Деплой

### Staging

```bash
git push origin develop  # Автоматический деплой через GitHub Actions
```

### Production

```bash
git push origin main     # Автоматический деплой через GitHub Actions
```

## 🤝 Разработка

### Git Flow

- `main` - продакшн
- `develop` - разработка
- `feature/*` - новые функции
- `hotfix/*` - критические исправления

### Code Style

- Backend: Black, isort, flake8
- Frontend: Prettier, ESLint

## 📞 Поддержка

Для вопросов и поддержки:

- Email: support@ai-sales-assistant.com
- Slack: #ai-sales-assistant
- Issues: GitHub Issues

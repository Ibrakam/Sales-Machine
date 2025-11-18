# API Документация

## Обзор

AI Sales Assistant предоставляет RESTful API для управления лидами, сообщениями, звонками и аналитикой.

**Base URL**: `http://localhost:8000/api/v1`

## Аутентификация

API использует JWT токены для аутентификации. Включите токен в заголовок `Authorization`:

```
Authorization: Bearer <your-access-token>
```

### Получение токена

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

## Endpoints

### Аутентификация

#### POST /auth/login
Вход в систему

#### POST /auth/refresh
Обновление access токена

#### POST /auth/logout
Выход из системы

#### GET /auth/me
Получение информации о текущем пользователе

### Пользователи

#### GET /users/
Получение списка пользователей (только для админов)

#### GET /users/me
Получение профиля текущего пользователя

#### PUT /users/me
Обновление профиля текущего пользователя

#### POST /users/
Создание нового пользователя (только для админов)

#### GET /users/{user_id}
Получение пользователя по ID

#### PUT /users/{user_id}
Обновление пользователя (только для админов)

#### DELETE /users/{user_id}
Удаление пользователя (только для админов)

### Лиды

#### GET /leads/
Получение списка лидов с фильтрацией

**Параметры запроса:**
- `skip` (int): Количество пропускаемых записей
- `limit` (int): Максимальное количество записей
- `search` (string): Поиск по имени, компании или email
- `status` (string): Фильтр по статусу
- `assigned_to` (int): Фильтр по назначенному пользователю
- `score_category` (string): Фильтр по категории скоринга

#### POST /leads/
Создание нового лида

#### GET /leads/{lead_id}
Получение лида по ID

#### PUT /leads/{lead_id}
Обновление лида

#### DELETE /leads/{lead_id}
Удаление лида (только для админов)

#### POST /leads/{lead_id}/score
AI-скоринг лида

### Сообщения

#### GET /messages/
Получение списка сообщений с фильтрацией

#### POST /messages/
Создание нового сообщения

#### GET /messages/{message_id}
Получение сообщения по ID

#### PUT /messages/{message_id}
Обновление сообщения

#### DELETE /messages/{message_id}
Удаление сообщения

#### POST /messages/{message_id}/send
Отправка сообщения

### CRM Интеграции

#### GET /crm/connections
Получение списка CRM подключений (только для админов)

#### POST /crm/connections
Создание нового CRM подключения (только для админов)

#### GET /crm/connections/{connection_id}
Получение CRM подключения по ID (только для админов)

#### PUT /crm/connections/{connection_id}
Обновление CRM подключения (только для админов)

#### DELETE /crm/connections/{connection_id}
Удаление CRM подключения (только для админов)

#### POST /crm/connections/{connection_id}/sync
Синхронизация данных с CRM (только для админов)

#### GET /crm/connections/{connection_id}/status
Получение статуса CRM подключения (только для админов)

### Прогнозы

#### GET /forecasts/
Получение списка прогнозов

#### POST /forecasts/
Создание нового прогноза (только для аналитиков и админов)

#### GET /forecasts/{forecast_id}
Получение прогноза по ID

#### PUT /forecasts/{forecast_id}
Обновление прогноза (только для аналитиков и админов)

#### DELETE /forecasts/{forecast_id}
Удаление прогноза (только для админов)

#### POST /forecasts/generate
Генерация нового прогноза с помощью AI (только для аналитиков и админов)

### Звонки

#### GET /calls/
Получение списка звонков с фильтрацией

#### POST /calls/
Создание нового звонка

#### GET /calls/{call_id}
Получение звонка по ID

#### PUT /calls/{call_id}
Обновление звонка

#### GET /calls/{call_id}/transcript
Получение транскрипта звонка

#### POST /calls/{call_id}/transcript
Создание транскрипта звонка

#### GET /calls/tasks
Получение списка задач по звонкам

#### POST /calls/tasks
Создание задачи по звонку

### AI Функции

#### POST /ai/generate-email
Генерация персонализированного email для лида

#### POST /ai/score-lead
AI-скоринг лида

#### POST /ai/analyze-call
AI-анализ звонка

#### POST /ai/generate-forecast
AI-генерация прогноза продаж (только для аналитиков и админов)

#### GET /ai/models
Получение списка доступных AI моделей

#### GET /ai/usage
Получение статистики использования AI

## Коды ошибок

- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `422` - Ошибка валидации
- `500` - Внутренняя ошибка сервера

## Пагинация

Для endpoints, возвращающих списки, используется пагинация:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

## Фильтрация и поиск

Многие endpoints поддерживают фильтрацию и поиск через query параметры:

- `search` - полнотекстовый поиск
- `status` - фильтр по статусу
- `assigned_to` - фильтр по назначенному пользователю
- `date_from` / `date_to` - фильтр по дате
- `sort` - сортировка (asc/desc)
- `order_by` - поле для сортировки

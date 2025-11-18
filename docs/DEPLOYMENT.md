# Руководство по развертыванию

## Локальная разработка

### Предварительные требования

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Быстрый старт

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd ai_agent
```

2. **Настройка переменных окружения**
```bash
# Backend
cp backend/env.example backend/.env
# Отредактируйте backend/.env с вашими настройками

# Frontend  
cp frontend/env.example frontend/.env.local
# Отредактируйте frontend/.env.local
```

3. **Запуск в режиме разработки**
```bash
# Запуск всех сервисов
docker-compose up -d

# Или запуск отдельных сервисов
docker-compose up -d postgres redis
cd backend && python -m uvicorn app.main:app --reload
cd frontend && npm run dev
```

4. **Доступ к приложению**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer (БД): http://localhost:8080

## Продакшн развертывание

### AWS EC2 (Ubuntu 22.04)

1. **Подготовка сервера**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка Nginx
sudo apt install nginx -y
```

2. **Настройка SSL (Let's Encrypt)**
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификата
sudo certbot --nginx -d yourdomain.com
```

3. **Настройка Nginx**
```nginx
# /etc/nginx/sites-available/ai-sales-assistant
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

4. **Создание продакшн docker-compose**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - NEXT_PUBLIC_API_URL=https://yourdomain.com/api
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - app-network

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - app-network
    command: celery -A app.celery worker --loglevel=info

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - app-network
    command: celery -A app.celery beat --loglevel=info

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

5. **Переменные окружения для продакшна**
```bash
# .env.prod
POSTGRES_DB=ai_sales_prod
POSTGRES_USER=ai_sales_user
POSTGRES_PASSWORD=strong_password_here
SECRET_KEY=very_strong_secret_key_here
OPENAI_API_KEY=your_openai_api_key
```

6. **Запуск продакшн версии**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Hetzner Cloud

1. **Создание сервера**
- Выберите Ubuntu 22.04
- Минимум 4GB RAM, 2 CPU
- 40GB SSD

2. **Настройка аналогично AWS EC2**

### CI/CD с GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/ai-sales-assistant
          git pull origin main
          docker-compose -f docker-compose.prod.yml down
          docker-compose -f docker-compose.prod.yml up -d --build
```

## Мониторинг

### Prometheus + Grafana

1. **Добавление в docker-compose**
```yaml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - app-network

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - app-network
```

2. **Настройка Prometheus**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
```

## Резервное копирование

### Автоматическое резервное копирование БД

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_NAME="ai_sales_prod"

# Создание резервной копии
docker exec postgres pg_dump -U ai_sales_user $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Удаление старых резервных копий (старше 7 дней)
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete

# Загрузка в S3 (опционально)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql s3://your-backup-bucket/
```

### Cron задача
```bash
# Добавить в crontab
0 2 * * * /opt/scripts/backup.sh
```

## Масштабирование

### Горизонтальное масштабирование

1. **Load Balancer (Nginx)**
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

upstream frontend {
    server frontend1:3000;
    server frontend2:3000;
}
```

2. **Масштабирование Celery**
```bash
# Запуск дополнительных воркеров
docker-compose up -d --scale celery_worker=3
```

## Безопасность

1. **Firewall**
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

2. **Fail2ban**
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

3. **Регулярные обновления**
```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

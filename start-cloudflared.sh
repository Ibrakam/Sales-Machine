#!/bin/bash

# Скрипт для запуска с Cloudflare Tunnel (cloudflared) - полностью бесплатно
# Можно запустить несколько туннелей одновременно

echo "🚀 Запуск AI Sales Assistant с Cloudflare Tunnel..."

# Проверка наличия cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Установка cloudflared..."
    brew install cloudflared
fi

# Запуск backend
echo "📦 Запуск backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 3

# Запуск cloudflared для backend
echo "🌐 Запуск Cloudflare Tunnel для backend (порт 8000)..."
cloudflared tunnel --url http://localhost:8000 > /tmp/cloudflared-backend.log 2>&1 &
CLOUDFLARED_BACKEND_PID=$!

sleep 5

# Получение URL из логов (cloudflared выводит URL в формате |  https://... |)
sleep 3
BACKEND_URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared-backend.log | head -1)

if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  Не удалось получить URL из логов автоматически"
    echo "📋 Проверьте вывод cloudflared вручную - URL должен быть в формате:"
    echo "   https://xxxxx.trycloudflare.com"
    echo "📋 Или проверьте логи: tail -f /tmp/cloudflared-backend.log"
    echo ""
    read -p "Введите URL backend вручную (или нажмите Enter для пропуска): " BACKEND_URL
    if [ -z "$BACKEND_URL" ]; then
        BACKEND_URL="https://your-backend-url.trycloudflare.com"
    fi
fi

echo "✅ Backend доступен по адресу: $BACKEND_URL"

# Обновление .env.local для frontend
echo "📝 Обновление frontend/.env.local..."
mkdir -p frontend
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > frontend/.env.local

# Запуск frontend в production режиме (для работы через cloudflared)
echo "📦 Сборка frontend для production..."
cd frontend

# Проверяем, есть ли уже собранная версия
if [ ! -d ".next" ] || [ "package.json" -nt ".next" ]; then
    echo "🔨 Сборка Next.js приложения..."
    npm run build
fi

echo "🚀 Запуск frontend в production режиме..."
npm start &
FRONTEND_PID=$!
cd ..

sleep 5

# Запуск cloudflared для frontend
echo "🌐 Запуск Cloudflare Tunnel для frontend (порт 3000)..."
cloudflared tunnel --url http://localhost:3000 > /tmp/cloudflared-frontend.log 2>&1 &
CLOUDFLARED_FRONTEND_PID=$!

sleep 5

# Получение URL из логов
sleep 3
FRONTEND_URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared-frontend.log | head -1)

if [ -z "$FRONTEND_URL" ]; then
    echo "⚠️  Не удалось получить URL из логов автоматически"
    echo "📋 Проверьте вывод cloudflared вручную - URL должен быть в формате:"
    echo "   https://xxxxx.trycloudflare.com"
    echo "📋 Или проверьте логи: tail -f /tmp/cloudflared-frontend.log"
    echo ""
    read -p "Введите URL frontend вручную (или нажмите Enter для пропуска): " FRONTEND_URL
    if [ -z "$FRONTEND_URL" ]; then
        FRONTEND_URL="https://your-frontend-url.trycloudflare.com"
    fi
fi

echo "✅ Frontend доступен по адресу: $FRONTEND_URL"
echo ""
echo "🎉 Готово! Дайте этот URL клиенту: $FRONTEND_URL"

echo ""
echo "📋 Для остановки нажмите Ctrl+C"

# Ожидание Ctrl+C
trap "echo '🛑 Остановка...'; kill $BACKEND_PID $FRONTEND_PID $CLOUDFLARED_BACKEND_PID $CLOUDFLARED_FRONTEND_PID 2>/dev/null; exit" INT
wait


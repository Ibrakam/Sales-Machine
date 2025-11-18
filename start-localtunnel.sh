#!/bin/bash

# Скрипт для запуска с localtunnel - полностью бесплатно
# Можно запустить несколько туннелей одновременно

echo "🚀 Запуск AI Sales Assistant с localtunnel..."

# Проверка наличия localtunnel
if ! command -v lt &> /dev/null; then
    echo "📦 Установка localtunnel..."
    npm install -g localtunnel
fi

# Запуск backend
echo "📦 Запуск backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 3

# Запуск localtunnel для backend
echo "🌐 Запуск localtunnel для backend (порт 8000)..."
lt --port 8000 --print-requests > /tmp/localtunnel-backend.log 2>&1 &
LT_BACKEND_PID=$!

sleep 5

# Получение URL из логов
BACKEND_URL=$(grep -o 'https://[^"]*\.loca\.lt' /tmp/localtunnel-backend.log | head -1)

if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  Не удалось получить URL из логов, проверьте вручную:"
    echo "   tail -f /tmp/localtunnel-backend.log"
    BACKEND_URL="https://your-backend-url.loca.lt"
fi

echo "✅ Backend доступен по адресу: $BACKEND_URL"

# Обновление .env.local для frontend
echo "📝 Обновление frontend/.env.local..."
mkdir -p frontend
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > frontend/.env.local

# Запуск frontend
echo "📦 Запуск frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

sleep 3

# Запуск localtunnel для frontend
echo "🌐 Запуск localtunnel для frontend (порт 3000)..."
lt --port 3000 --print-requests > /tmp/localtunnel-frontend.log 2>&1 &
LT_FRONTEND_PID=$!

sleep 5

# Получение URL из логов
FRONTEND_URL=$(grep -o 'https://[^"]*\.loca\.lt' /tmp/localtunnel-frontend.log | head -1)

if [ -z "$FRONTEND_URL" ]; then
    echo "⚠️  Не удалось получить URL из логов, проверьте вручную:"
    echo "   tail -f /tmp/localtunnel-frontend.log"
    FRONTEND_URL="https://your-frontend-url.loca.lt"
else
    echo "✅ Frontend доступен по адресу: $FRONTEND_URL"
    echo ""
    echo "🎉 Готово! Дайте этот URL клиенту: $FRONTEND_URL"
fi

echo ""
echo "📋 Для остановки нажмите Ctrl+C"

# Ожидание Ctrl+C
trap "echo '🛑 Остановка...'; kill $BACKEND_PID $FRONTEND_PID $LT_BACKEND_PID $LT_FRONTEND_PID 2>/dev/null; exit" INT
wait


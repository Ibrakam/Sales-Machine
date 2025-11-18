#!/bin/bash

# Скрипт для быстрого запуска с ngrok

echo "🚀 Запуск AI Sales Assistant с ngrok..."

# Проверка наличия ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен. Установите: brew install ngrok"
    exit 1
fi

# Запуск backend
echo "📦 Запуск backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 3

# Запуск ngrok для backend
echo "🌐 Запуск ngrok для backend (порт 8000)..."
ngrok http 8000 > /tmp/ngrok-backend.log &
NGROK_BACKEND_PID=$!

sleep 5

# Получение URL из ngrok
BACKEND_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok[^"]*' | head -1)

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Не удалось получить ngrok URL для backend"
    kill $BACKEND_PID $NGROK_BACKEND_PID 2>/dev/null
    exit 1
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

# Запуск ngrok для frontend
echo "🌐 Запуск ngrok для frontend (порт 3000)..."
ngrok http 3000 > /tmp/ngrok-frontend.log &
NGROK_FRONTEND_PID=$!

sleep 5

# Получение URL из ngrok
FRONTEND_URL=$(curl -s http://localhost:4041/api/tunnels | grep -o 'https://[^"]*\.ngrok[^"]*' | head -1)

if [ -z "$FRONTEND_URL" ]; then
    echo "⚠️  Не удалось получить ngrok URL для frontend (возможно, используется другой порт)"
    echo "📋 Проверьте вручную: http://localhost:4041"
else
    echo "✅ Frontend доступен по адресу: $FRONTEND_URL"
    echo ""
    echo "🎉 Готово! Дайте этот URL клиенту: $FRONTEND_URL"
fi

echo ""
echo "📋 Для остановки нажмите Ctrl+C"
echo "📋 Backend панель: http://localhost:4040"
echo "📋 Frontend панель: http://localhost:4041"

# Ожидание Ctrl+C
trap "echo '🛑 Остановка...'; kill $BACKEND_PID $FRONTEND_PID $NGROK_BACKEND_PID $NGROK_FRONTEND_PID 2>/dev/null; exit" INT
wait


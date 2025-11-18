#!/bin/bash

# Скрипт для запуска с одним ngrok (только для backend)
# Frontend можно развернуть на Vercel или запустить локально

echo "🚀 Запуск AI Sales Assistant с одним ngrok..."

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
NGROK_PID=$!

sleep 5

# Получение URL из ngrok
BACKEND_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok[^"]*' | head -1)

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Не удалось получить ngrok URL для backend"
    kill $BACKEND_PID $NGROK_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend доступен по адресу: $BACKEND_URL"
echo ""
echo "📋 Варианты для frontend:"
echo "   1. Развернуть на Vercel (рекомендуется) - см. README_DEPLOY.md"
echo "   2. Запустить локально (см. ниже)"
echo ""

# Обновление .env.local для frontend
echo "📝 Обновление frontend/.env.local..."
mkdir -p frontend
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > frontend/.env.local

# Запуск frontend локально
read -p "Запустить frontend локально? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Запуск frontend локально..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ Frontend запущен локально на http://localhost:3000"
    echo "📋 Откройте http://localhost:3000 в браузере"
    echo "📋 Или используйте другой туннель для frontend (см. альтернативы ниже)"
else
    echo "📋 Для развертывания frontend на Vercel:"
    echo "   1. Зайдите на vercel.com"
    echo "   2. Импортируйте репозиторий"
    echo "   3. Установите переменную: NEXT_PUBLIC_API_URL=$BACKEND_URL"
fi

echo ""
echo "📋 Backend панель ngrok: http://localhost:4040"
echo "📋 Для остановки нажмите Ctrl+C"

# Ожидание Ctrl+C
trap "echo '🛑 Остановка...'; kill $BACKEND_PID $NGROK_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait


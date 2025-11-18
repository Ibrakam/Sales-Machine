# 🔄 Обновление URL Backend

## ✅ URL обновлен!

Новый URL backend: `https://infectious-rim-ser-robot.trycloudflare.com`

Файл `frontend/.env.local` обновлен.

## 🔄 Перезапуск Frontend

Чтобы изменения вступили в силу, нужно перезапустить frontend:

### Если frontend запущен в dev режиме:
```bash
# Остановите текущий процесс (Ctrl+C)
# Затем запустите заново:
cd frontend
npm run dev
```

### Если frontend запущен в production режиме:
```bash
# Остановите текущий процесс (Ctrl+C)
# Затем запустите заново:
cd frontend
npm start
```

### Или используйте скрипт:
```bash
./start-cloudflared.sh
```

## ✅ Проверка

После перезапуска frontend будет обращаться к:
- Backend API: `https://infectious-rim-ser-robot.trycloudflare.com`
- API Docs: `https://infectious-rim-ser-robot.trycloudflare.com/docs`
- Health Check: `https://infectious-rim-ser-robot.trycloudflare.com/health`

## 🔍 Если не работает

1. Убедитесь, что frontend перезапущен
2. Проверьте консоль браузера на ошибки CORS
3. Убедитесь, что backend доступен по новому URL
4. Проверьте, что в `frontend/.env.local` правильный URL


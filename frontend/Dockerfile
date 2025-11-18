FROM node:18-alpine

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production

# Копирование исходного кода
COPY . .

# Создание пользователя для безопасности
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Изменение владельца файлов
RUN chown -R nextjs:nodejs /app
USER nextjs

# Открытие порта
EXPOSE 3000

# Команда по умолчанию
CMD ["npm", "run", "dev"]

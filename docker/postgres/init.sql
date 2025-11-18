-- Инициализация базы данных AI Sales Assistant

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Создание индексов для полнотекстового поиска
-- (будут созданы автоматически через SQLAlchemy)

-- Настройки для производительности
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET pg_stat_statements.track = 'all';

-- Создание пользователя для приложения (если не существует)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ai_sales_user') THEN
        CREATE ROLE ai_sales_user WITH LOGIN PASSWORD 'ai_sales_password';
    END IF;
END
$$;

-- Предоставление прав
GRANT ALL PRIVILEGES ON DATABASE ai_sales_db TO ai_sales_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO ai_sales_user;

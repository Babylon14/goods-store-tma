# Используем стабильный образ Python
FROM python:3.12-slim-bookworm

# Устанавливаем системные зависимости (если понадобятся для компиляции библиотек)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv для управления зависимостями
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Рабочая директория внутри контейнера
WORKDIR /app

# 1. Сначала копируем только файлы зависимостей
# Это позволяет Docker кешировать установленные библиотеки
COPY pyproject.toml uv.lock ./

# 2. Устанавливаем зависимости (создастся папка .venv)
RUN uv sync --frozen --no-cache

# 3. Копируем конфигурацию Alembic и переменные окружения из корня
COPY alembic.ini .env ./

# 4. Копируем папку с миграциями
# Учитываем, что на диске она лежит в backend/migrations
COPY backend/migrations ./backend/migrations

# 5. Копируем исходный код бэкенда
COPY backend/src ./src

# Добавляем виртуальное окружение в PATH
ENV PATH="/app/.venv/bin:$PATH"
# Отключаем генерацию .pyc файлов и включаем буферизацию логов
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Открываем порт
EXPOSE 8000

# Запуск приложения
CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]


# Используем легковесный образ Python
FROM python:3.12-slim-bookworm

# Устанавливаем uv напрямую через бинарный файл для скорости
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# 1. Копируем файлы зависимостей из КОРНЯ проекта
# (В контексте docker-compose это пути относительно корня)
COPY pyproject.toml uv.lock ./

# 2. Устанавливаем зависимости
# --frozen гарантирует, что uv.lock не будет изменен
# --no-cache уменьшает размер итогового образа
RUN uv sync --frozen --no-cache

# 3. Копируем весь исходный код бекенда
# В твоей структуре это папка backend/src
COPY backend/src ./src

# 4. Копируем .env файл (опционально, если не прокидываем через compose)
COPY .env .env

# Добавляем путь к установленному окружению в PATH, 
# чтобы команды типа "fastapi" или "celery" работали напрямую
ENV PATH="/app/.venv/bin:$PATH"

# По умолчанию запускаем FastAPI
# Используем флаг --proxy-headers, так как в будущем может быть Nginx
CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]


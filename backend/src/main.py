import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.endpoints.products_api import router as product_router
from src.api.v1.endpoints.orders_api import router as order_router

load_dotenv()

# Получаем ссылку, если её нет — ставим localhost по умолчанию
APP_URL = os.getenv("APP_URL", "http://localhost").strip()

app = FastAPI(title="Goods Store TMA API", version="1.0.0")

# Список разрешенных адресов
origins = [
    "http://localhost",          # Доступ через Nginx локально
    "http://localhost:5173",     # Прямой доступ к Vite (на всякий случай)
    "http://127.0.0.1",          # Доступ через IP локально
    APP_URL,     # Доступ через текущий туннель zrok
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # Разрешаем запросы с этих адресов
    allow_credentials=True,
    allow_methods=["*"],               # Разрешаем все методы (GET, POST и т.д.)
    allow_headers=["*"],               # Разрешаем все заголовки
)

# Создаем папку для загрузок, если её нет
UPLOAD_DIR = "/app/backend/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# говорим FastAPI, что всё, что летит на /static, нужно искать в папке uploads
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")
# Подключаем роутер с префиксом
app.include_router(product_router, prefix="/api/v1/products", tags=["Продукты"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["Заказы"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}


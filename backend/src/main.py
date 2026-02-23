import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api.v1.endpoints.products_api import router as product_router


tags_metadata = [
    {
        "name": "Продукты",
        "description": "Управление товарами магазина: создание, удаление, обновление и просмотр.",
    },
]

app = FastAPI(
    title="Goods Store TMA API",
    version="1.0.0",
    openapi_tags=tags_metadata
    )

# Создаем папку для загрузок, если её нет
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Монтируем папку со статикой
# Теперь файл uploads/items/photo.jpg будет доступен по ссылке http://localhost:8000/static/items/photo.jpg
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")
# Подключаем роутер с префиксом
app.include_router(product_router, prefix="/api/v1/products")


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}


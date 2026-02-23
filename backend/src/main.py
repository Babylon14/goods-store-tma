from fastapi import FastAPI
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

# Подключаем роутер с префиксом
app.include_router(product_router, prefix="/api/v1/products")


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}


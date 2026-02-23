from fastapi import FastAPI
from src.api.v1.endpoints.products_api import router as product_router


app = FastAPI(title="Goods Store TMA API", version="1.0.0")

# Подключаем роутер с префиксом
app.include_router(product_router, prefix="/api/v1/products", tags=["Products"])


@app.get("/")
async def root():
    return {"message": "Hello World"}


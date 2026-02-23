from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.product_schema import ProductCreate, ProductRead, ProductUpdate
from src.repositories.product_repository import ProductRepository
from backend.src.api.dependencies import get_product_repo


router = APIRouter()

@router.post(path="/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    product_repo: ProductRepository = Depends(get_product_repo)
):
    """Создать новый товар. Принимает данные товара и список вариантов (объемов)."""
    return await product_repo.create_with_variants(product_in.model_dump())


@router.get(path="/", response_model=List[ProductRead])
async def get_list_products(
    skip: int = 0,
    limit: int = 100,
    product_repo: ProductRepository = Depends(get_product_repo)
):
    """Получить список всех товаров с вложенными вариантами. (пагинация)."""
    return await product_repo.get_multi_with_variants(skip=skip, limit=limit)


@router.get(path="/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    product_repo: ProductRepository = Depends(get_product_repo)
):
    """Получить один товар со всеми его вариантами по ID."""
    return await product_repo.get_with_variants(product_id=product_id)


@router.patch(path="/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    product_repo: ProductRepository = Depends(get_product_repo)
):
    """Обновить данные товара (название, описание и т.д.).
    Использует метод update из базового репозитория."""
    product = await product_repo.get(product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")


@router.delete(path="/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    product_repo: ProductRepository = Depends(get_product_repo)
):
    """Удалить товар по ID."""
    success = await product_repo.delete(product_id=product_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    return None

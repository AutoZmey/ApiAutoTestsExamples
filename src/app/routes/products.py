from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.app import database
from src.app.models import ProductCreate, ProductResponse, ProductUpdate, UserResponse
from src.app.security import get_current_user, require_admin

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    active_only: bool = Query(True),
):
    return database.get_products(category=category, search=search, active_only=active_only)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    product = database.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product #{product_id} not found",
        )
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    req: ProductCreate,
    current_user: UserResponse = Depends(require_admin),
):
    existing = [p for p in database.get_products(active_only=False) if p.sku.lower() == req.sku.lower()]
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{req.sku}' already exists",
        )

    return database.create_product(
        title=req.title,
        sku=req.sku,
        category=req.category,
        price=req.price,
        stock=req.stock,
        description=req.description or "",
    )


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    req: ProductUpdate,
    current_user: UserResponse = Depends(require_admin),
):
    product = database.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product #{product_id} not found",
        )

    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    updated = database.update_product(product_id, updates)
    return updated


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: UserResponse = Depends(require_admin),
):
    product = database.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product #{product_id} not found",
        )

    database.delete_product(product_id)
    return None

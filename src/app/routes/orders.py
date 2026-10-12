from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.app import database
from src.app.models import OrderCreate, OrderResponse, OrderStatus, OrderStatusUpdate, Role, UserResponse
from src.app.security import get_current_user, require_admin

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    req: OrderCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        order = database.create_order(
            user_id=current_user.id,
            user_email=current_user.email,
            items_req=[item.model_dump() for item in req.items],
            shipping_address=req.shipping_address,
        )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=List[OrderResponse])
def list_orders(
    current_user: UserResponse = Depends(get_current_user),
):
    if current_user.role == Role.ADMIN:
        return database.list_orders(user_id=None)
    return database.list_orders(user_id=current_user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: UserResponse = Depends(get_current_user),
):
    order = database.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} not found",
        )

    if current_user.role != Role.ADMIN and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this order",
        )

    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    req: OrderStatusUpdate,
    current_user: UserResponse = Depends(require_admin),
):
    order = database.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} not found",
        )

    updated = database.update_order_status(order_id, req.status)
    return updated


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    current_user: UserResponse = Depends(get_current_user),
):
    order = database.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} not found",
        )

    if current_user.role != Role.ADMIN and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this order",
        )

    try:
        cancelled = database.cancel_order(order_id)
        return cancelled
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

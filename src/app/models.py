from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# Auth Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: Optional[Role] = Role.USER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    created_at: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Product Models
class ProductCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    sku: str = Field(..., min_length=3, max_length=50)
    category: str = Field(..., min_length=2, max_length=50)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: Optional[str] = ""


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=120)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    title: str
    sku: str
    category: str
    price: float
    stock: int
    description: str
    is_active: bool
    created_at: str


# Order Models
class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    product_id: int
    product_title: str
    unit_price: float
    quantity: int
    subtotal: float


class OrderCreate(BaseModel):
    items: List[OrderItemRequest] = Field(..., min_length=1)
    shipping_address: str = Field(..., min_length=5, max_length=250)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    user_id: int
    user_email: str
    items: List[OrderItemResponse]
    status: OrderStatus
    shipping_address: str
    subtotal: float
    tax: float
    total: float
    created_at: str


# Analytics Models
class AnalyticsSummary(BaseModel):
    total_orders: int
    total_revenue: float
    pending_orders: int
    shipped_orders: int
    total_products: int
    low_stock_products: int

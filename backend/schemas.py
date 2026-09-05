from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
class UserLogin(BaseModel):
    email: EmailStr
    password: str
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    created_at: datetime
class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_name: str
    product_link: str | None
    size: str | None
    color: str | None
    notes: str | None
    created_at: datetime
class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_name: str
    product_link: str | None
    size: str | None
    color: str | None
    notes: str | None
class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    payment_method: str
    payment_status: str
    email_status: str
    created_at: datetime
    items: list[OrderItemResponse]
class OrderStatusUpdate(BaseModel):
    status: str
class PaymentStatusUpdate(BaseModel):
    payment_status: str

class ContactRequest(BaseModel):
    subject: str
    message: str

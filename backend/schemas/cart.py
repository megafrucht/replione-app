from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CartItemCreate(BaseModel):
    product_name: str
    screenshot_id: str
    product_link: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None

class CartItemResponse(CartItemCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

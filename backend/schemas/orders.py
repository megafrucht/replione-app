from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    screenshot_id: str
    product_link: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    payment_method: str
    payment_status: str
    created_at: datetime
    items: List[OrderItemResponse]
    class Config:
        from_attributes = True

class OrderUpdate(BaseModel):
    status: str

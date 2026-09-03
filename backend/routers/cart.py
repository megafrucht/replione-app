from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database import models
from backend.schemas.cart import CartItemCreate, CartItemResponse
from backend.core.security import get_current_user_id

router = APIRouter(prefix="/api/cart", tags=["cart"])

@router.get("", response_model=list[CartItemResponse])
def get_cart(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    return items

@router.post("/items", response_model=CartItemResponse)
def add_to_cart(item: CartItemCreate, request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)

    if not item.product_name or not item.screenshot_id:
        raise HTTPException(status_code=400, detail="Produktname und Screenshot sind zwingend erforderlich.")

    db_item = models.CartItem(
        user_id=user_id,
        product_name=item.product_name,
        screenshot_id=item.screenshot_id,
        product_link=item.product_link,
        size=item.size,
        color=item.color,
        notes=item.notes
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


from pydantic import BaseModel
from typing import Optional

class CartItemUpdate(BaseModel):
    product_name: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None

@router.patch("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item(item_id: int, data: CartItemUpdate, request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    item = db.query(models.CartItem).filter(models.CartItem.id == item_id, models.CartItem.user_id == user_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")

    if data.product_name is not None:
        if not data.product_name.strip():
             raise HTTPException(status_code=400, detail="Produktname darf nicht leer sein.")
        item.product_name = data.product_name

    if data.size is not None: item.size = data.size
    if data.color is not None: item.color = data.color
    if data.notes is not None: item.notes = data.notes

    db.commit()
    db.refresh(item)
    return item

@router.delete("/items/{item_id}")
def remove_from_cart(item_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    item = db.query(models.CartItem).filter(models.CartItem.id == item_id, models.CartItem.user_id == user_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    db.delete(item)
    db.commit()
    return {"message": "Artikel entfernt"}

@router.delete("")
def clear_cart(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()
    return {"message": "Warenkorb geleert"}

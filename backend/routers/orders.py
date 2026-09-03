import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database import models
from backend.schemas.orders import OrderResponse
from backend.core.security import get_current_user_id

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/checkout", response_model=OrderResponse)
def checkout(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)

    # Load cart items
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Der Warenkorb ist leer.")

    # Create order
    order_num = f"RPL-{uuid.uuid4().hex[:8].upper()}"
    new_order = models.Order(
        order_number=order_num,
        user_id=user_id,
        status="Eingegangen",
        payment_method="cash",
        payment_status="offen",
        email_status="pending"
    )
    db.add(new_order)
    db.flush() # get ID without committing fully

    # Create order items snapshots
    for item in cart_items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_name=item.product_name,
            screenshot_id=item.screenshot_id,
            product_link=item.product_link,
            size=item.size,
            color=item.color,
            notes=item.notes
        )
        db.add(order_item)

    # Clear cart
    for item in cart_items:
        db.delete(item)

    db.commit()
    db.refresh(new_order)

    # TODO: Trigger Email via background task or service
    from backend.services.email_service import send_order_confirmation
    user = db.query(models.User).filter(models.User.id == user_id).first()
    send_order_confirmation(user.email, user.name, order_num, len(cart_items))

    return new_order

@router.get("/my", response_model=list[OrderResponse])
def get_my_orders(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.created_at.desc()).all()
    return orders

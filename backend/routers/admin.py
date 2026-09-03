import urllib.parse
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database import models
from backend.core.config import ADMIN_PASSWORD
from backend.core.security import verify_admin_token

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/login")
def admin_login(x_admin_password: str = Header(None)):
    if x_admin_password:
        x_admin_password = urllib.parse.unquote(x_admin_password)

    if not x_admin_password or x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    import datetime
    import jwt
    from backend.core.config import SECRET_KEY, ALGORITHM
    from fastapi import Response

    payload = {
        "role": "admin",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    response = Response(content='{"status":"ok"}', media_type="application/json")
    response.set_cookie(key="admin_access_token", value=token, httponly=True, max_age=86400, samesite="lax", secure=True)
    return response


@router.post("/logout")
def admin_logout():
    from fastapi import Response
    response = Response(content='{"status":"ok"}', media_type="application/json")
    response.delete_cookie(key="admin_access_token")
    return response

@router.get("/check")
def admin_check(request: Request, _: bool = Depends(verify_admin_token)):
    return {"status": "ok"}

@router.get("/orders")
def get_all_orders(request: Request, db: Session = Depends(get_db), _: bool = Depends(verify_admin_token)):
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    result = []
    for o in orders:
        items = [{"product_name": i.product_name, "screenshot_id": i.screenshot_id, "size": i.size, "color": i.color, "notes": i.notes, "product_link": i.product_link} for i in o.items]
        user = db.query(models.User).filter(models.User.id == o.user_id).first()
        result.append({
            "id": o.id,
            "order_number": o.order_number,
            "user_id": o.user_id,
            "user_name": user.name if user else "Unknown",
            "user_email": user.email if user else "Unknown",
            "status": o.status,
            "payment_method": o.payment_method,
            "payment_status": o.payment_status,
            "items": items,
            "created_at": o.created_at.isoformat()
        })
    return result

from backend.schemas.orders import OrderUpdate

@router.patch("/orders/{order_number}/status")
def update_order_status(order_number: str, data: OrderUpdate, request: Request, db: Session = Depends(get_db), _: bool = Depends(verify_admin_token)):
    order = db.query(models.Order).filter(models.Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    valid_statuses = ["Eingegangen", "In Bearbeitung", "Bestellt", "Unterwegs", "Abgeschlossen"]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Ungültiger Status")

    order.status = data.status
    db.commit()

    from backend.services.email_service import send_status_update
    user = db.query(models.User).filter(models.User.id == order.user_id).first()
    if user:
        send_status_update(user.email, user.name, order.order_number, data.status)
    return {"message": "Status aktualisiert"}

@router.get("/users")
def get_all_users(request: Request, db: Session = Depends(get_db), _: bool = Depends(verify_admin_token)):
    users = db.query(models.User).all()
    result = []
    for u in users:
        order_count = db.query(models.Order).filter(models.Order.user_id == u.id).count()
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "created_at": u.created_at.isoformat(),
            "order_count": order_count
        })
    return result

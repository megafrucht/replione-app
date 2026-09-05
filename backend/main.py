from contextlib import asynccontextmanager
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import or_
from sqlalchemy.orm import Session
from . import models
from .auth import (
    clear_session_cookie,
    create_session_token,
    decode_session_token,
    get_current_user,
    hash_password,
    require_admin,
    set_session_cookie,
    verify_password,
)
from .config import settings
from .database import Base, engine, get_db
from .email_bot import send_order_email, send_admin_contact_email
from .schemas import (
    OrderStatusUpdate,
    PaymentStatusUpdate,
    UserLogin,
    UserRegister,
    ContactRequest,
)
from .storage import (
    delete_screenshot,
    download_screenshot,
    upload_screenshot,
)
ORDER_STATUSES = {
    "Eingegangen",
    "In Bearbeitung",
    "Bestellt",
    "Unterwegs",
    "Abgeschlossen",
    "Storniert",
}
PAYMENT_STATUSES = {
    "offen",
    "bezahlt",
}
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NOT NULL DEFAULT '';"))
    except: pass
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS email_status VARCHAR(50) NOT NULL DEFAULT 'pending';"))
    except: pass
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE order_items ADD COLUMN IF NOT EXISTS screenshot_path TEXT NOT NULL DEFAULT '';"))
    except: pass
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE orders DROP COLUMN IF EXISTS order_number;"))
    except: pass
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE orders DROP COLUMN IF EXISTS items;"))
    except: pass
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE order_items DROP COLUMN IF EXISTS screenshot_id;"))
    except: pass
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE cart_items DROP COLUMN IF EXISTS screenshot_id;"))
    except: pass
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "replione",
        "version": settings.APP_VERSION,
    }
@app.post("/api/auth/register")
def register(
    data: UserRegister,
    response: Response,
    db: Session = Depends(get_db),
):
    name = data.name.strip()
    email = data.email.lower().strip()
    if len(name) < 2:
        raise HTTPException(
            status_code=400,
            detail="Bitte gib deinen Namen ein.",
        )
    if len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Das Passwort muss mindestens 8 Zeichen lang sein.",
        )
    existing = (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Diese E-Mail-Adresse ist bereits registriert.",
        )
    user = models.User(
        name=name,
        email=email,
        password_hash=hash_password(data.password),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_session_token(
        user.id,
        user.is_admin,
    )
    set_session_cookie(response, token)
    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin,
        },
    }
@app.post("/api/auth/login")
def login(
    data: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    email = data.email.lower().strip()
    user = (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )
    if not user or not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="E-Mail oder Passwort ist falsch.",
        )
    token = create_session_token(
        user.id,
        user.is_admin,
    )
    set_session_cookie(response, token)
    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin,
        },
    }
@app.post("/api/auth/admin-login")
def admin_login(
    response: Response,
    password: str = Form(...),
):
    if not settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_PASSWORD ist nicht konfiguriert.",
        )
    if password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Admin-Passwort ist falsch.",
        )
    token = create_session_token(
        0,
        True,
    )
    set_session_cookie(response, token)
    return {
        "success": True,
        "admin": True,
    }
@app.post("/api/auth/logout")
def logout(response: Response):
    clear_session_cookie(response)
    return {
        "success": True,
    }
@app.get("/api/auth/me")
def current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.cookies.get("replione_session")
    if token:
        payload = decode_session_token(token)
        if payload and payload.get("admin") is True:
            return {
                "authenticated": True,
                "is_admin": True,
                "user": None,
            }
    user = get_current_user(request, db)
    return {
        "authenticated": True,
        "is_admin": user.is_admin,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }
@app.get("/api/cart")
def get_cart(
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == user.id)
        .order_by(models.CartItem.created_at.desc())
        .all()
    )
    return {
        "items": [
            {
                "id": item.id,
                "product_name": item.product_name,
                "product_link": item.product_link,
                "size": item.size,
                "color": item.color,
                "notes": item.notes,
                "created_at": item.created_at,
            }
            for item in items
        ]
    }
@app.post("/api/cart/items")
async def add_cart_item(
    request: Request,
    product_name: str = Form(...),
    screenshot: UploadFile = File(...),
    product_link: str | None = Form(None),
    size: str | None = Form(None),
    color: str | None = Form(None),
    notes: str | None = Form(None),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    product_name = product_name.strip()
    if not product_name:
        raise HTTPException(
            status_code=400,
            detail="Produktname ist erforderlich.",
        )
    screenshot_path = await upload_screenshot(
        screenshot,
        user.id,
    )
    item = models.CartItem(
        user_id=user.id,
        product_name=product_name,
        product_link=product_link.strip() if product_link else None,
        size=size.strip() if size else None,
        color=color.strip() if color else None,
        notes=notes.strip() if notes else None,
        screenshot_path=screenshot_path,
    )
    import logging
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
    except Exception as exc:
        db.rollback()
        logging.exception("Database INSERT Error for cart item:")
        delete_screenshot(screenshot_path)
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Speichern des Artikels in der Datenbank.",
        )
    return {
        "success": True,
        "item": {
            "id": item.id,
            "product_name": item.product_name,
            "product_link": item.product_link,
            "size": item.size,
            "color": item.color,
            "notes": item.notes,
            "created_at": item.created_at,
        },
    }
@app.delete("/api/cart/items/{item_id}")
def delete_cart_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.id == item_id,
            models.CartItem.user_id == user.id,
        )
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Warenkorb-Artikel nicht gefunden.",
        )
    screenshot_path = item.screenshot_path
    db.delete(item)
    db.commit()
    delete_screenshot(screenshot_path)
    return {
        "success": True,
    }
@app.get("/api/cart/items/{item_id}/screenshot")
def cart_screenshot(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.id == item_id,
            models.CartItem.user_id == user.id,
        )
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Screenshot nicht gefunden.",
        )
    data = download_screenshot(item.screenshot_path)
    return Response(
        content=data,
        media_type="image/*",
    )
@app.get("/api/orders/{order_id}/items/{item_id}/screenshot")
def order_screenshot(
    order_id: int,
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Bestellung nicht gefunden.",
        )
    if not user.is_admin and order.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Zugriff verweigert.",
        )
    item = (
        db.query(models.OrderItem)
        .filter(
            models.OrderItem.id == item_id,
            models.OrderItem.order_id == order_id,
        )
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Bestellartikel nicht gefunden.",
        )
    data = download_screenshot(item.screenshot_path)
    return Response(
        content=data,
        media_type="image/*",
    )
@app.post("/api/orders/checkout")
def checkout(
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    cart_items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == user.id)
        .order_by(models.CartItem.created_at.asc())
        .all()
    )
    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Dein Warenkorb ist leer.",
        )
    try:
        order = models.Order(
            user_id=user.id,
            status="Eingegangen",
            payment_method="Barzahlung",
            payment_status="offen",
            email_status="pending",
        )
        db.add(order)
        db.flush()
        for cart_item in cart_items:
            db.add(
                models.OrderItem(
                    order_id=order.id,
                    product_name=cart_item.product_name,
                    product_link=cart_item.product_link,
                    size=cart_item.size,
                    color=cart_item.color,
                    notes=cart_item.notes,
                    screenshot_path=cart_item.screenshot_path,
                )
            )
        for cart_item in cart_items:
            db.delete(cart_item)
        db.commit()
    except Exception as exc:
        db.rollback()
        import logging
        logging.exception("Checkout DB Error:")
        raise HTTPException(
            status_code=500,
            detail="Bestellung konnte nicht erstellt werden.",
        )
    try:
        email_sent = send_order_email(
            recipient=user.email,
            order_id=order.id,
            customer_name=user.name,
        )
        order.email_status = "sent" if email_sent else "failed"
        db.commit()
    except Exception as exc:
        db.rollback()
        import logging
        logging.exception("Checkout Email Update Error:")
    return {
        "success": True,
        "order_id": order.id,
        "status": order.status,
        "payment_method": order.payment_method,
    }
@app.get("/api/orders")
def get_orders(
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    orders = (
        db.query(models.Order)
        .filter(models.Order.user_id == user.id)
        .order_by(models.Order.created_at.desc())
        .all()
    )
    return {
        "orders": [
            {
                "id": order.id,
                "status": order.status,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "email_status": order.email_status,
                "created_at": order.created_at,
                "items": [
                    {
                        "id": item.id,
                        "product_name": item.product_name,
                        "product_link": item.product_link,
                        "size": item.size,
                        "color": item.color,
                        "notes": item.notes,
                    }
                    for item in order.items
                ],
            }
            for order in orders
        ]
    }
@app.get("/api/orders/{order_id}")
def get_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Bestellung nicht gefunden.",
        )
    if not user.is_admin and order.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Zugriff verweigert.",
        )
    return {
        "id": order.id,
        "status": order.status,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "email_status": order.email_status,
        "created_at": order.created_at,
        "items": [
            {
                "id": item.id,
                "product_name": item.product_name,
                "product_link": item.product_link,
                "size": item.size,
                "color": item.color,
                "notes": item.notes,
            }
            for item in order.items
        ],
    }
@app.get("/api/admin/orders")
def admin_orders(
    request: Request,
    search: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    require_admin(request, db)
    query = db.query(
        models.Order
    ).join(
        models.User
    )
    if search:
        search_value = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.User.name.ilike(search_value),
                models.User.email.ilike(search_value),
                models.Order.id.cast(
                    models.String
                ).ilike(search_value),
            )
        )
    if status:
        query = query.filter(
            models.Order.status == status
        )
    orders = (
        query
        .order_by(models.Order.created_at.desc())
        .all()
    )
    return {
        "orders": [
            {
                "id": order.id,
                "customer": {
                    "id": order.user.id,
                    "name": order.user.name,
                    "email": order.user.email,
                },
                "status": order.status,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "email_status": order.email_status,
                "created_at": order.created_at,
                "items": [
                    {
                        "id": item.id,
                        "product_name": item.product_name,
                        "product_link": item.product_link,
                        "size": item.size,
                        "color": item.color,
                        "notes": item.notes,
                    }
                    for item in order.items
                ],
            }
            for order in orders
        ]
    }
@app.patch("/api/admin/orders/{order_id}/status")
def admin_update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin(request, db)
    if data.status not in ORDER_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Ungültiger Bestellstatus.",
        )
    order = db.get(
        models.Order,
        order_id,
    )
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Bestellung nicht gefunden.",
        )
    order.status = data.status
    db.commit()
    return {
        "success": True,
        "order_id": order.id,
        "status": order.status,
    }
@app.patch("/api/admin/orders/{order_id}/payment")
def admin_update_payment_status(
    order_id: int,
    data: PaymentStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin(request, db)
    if data.payment_status not in PAYMENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Ungültiger Zahlungsstatus.",
        )
    order = db.get(
        models.Order,
        order_id,
    )
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Bestellung nicht gefunden.",
        )
    order.payment_status = data.payment_status
    db.commit()
    return {
        "success": True,
        "order_id": order.id,
        "payment_status": order.payment_status,
    }
import mimetypes
mimetypes.add_type("text/html", ".html")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")

@app.post("/api/admin/orders/{order_id}/contact")
def admin_contact_order(
    order_id: int,
    data: ContactRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin(request, db)
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Bestellung nicht gefunden.")

    success = send_admin_contact_email(
        recipient=order.user.email,
        subject=data.subject,
        body=data.message,
        customer_name=order.user.name
    )
    if not success:
        raise HTTPException(status_code=500, detail="E-Mail konnte nicht gesendet werden. SMTP Fehler.")
    return {"success": True}

@app.get("/api/admin/users")
def admin_users(
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin(request, db)
    users = db.query(models.User).order_by(models.User.created_at.desc()).all()

    from sqlalchemy import func
    return {
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "created_at": u.created_at,
                "order_count": db.query(func.count(models.Order.id)).filter(models.Order.user_id == u.id).scalar()
            } for u in users
        ]
    }

app.mount(
    "/",
    StaticFiles(
        directory="static",
        html=True,
    ),
    name="static",
)

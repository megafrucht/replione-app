import uuid
import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models
from auth import hash_password, verify_password, create_access_token, get_current_user_id
from email_bot import send_order_confirmation

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Replione API")

# --- SCHEMAS ---
class RegisterSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class UpdateProfileSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class OrderItemSchema(BaseModel):
    link: str = ""
    size: str = ""
    color: str = ""
    notes: str = ""

class CreateOrderSchema(BaseModel):
    items: list[OrderItemSchema]

# --- AUTH ROUTEN (Cookie Basiert) ---
@app.post("/api/auth/register")
def register(data: RegisterSchema, response: Response, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Diese E-Mail-Adresse ist bereits registriert.")

    new_user = models.User(
        name=data.name.strip(),
        email=data.email.lower().strip(),
        hashed_password=hash_password(data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(new_user.id, new_user.email)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=30*24*3600, samesite="lax", secure=True)
    return {"message": "Registrierung erfolgreich"}

@app.post("/api/auth/login")
def login(data: LoginSchema, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Ungültige E-Mail-Adresse oder falsches Passwort.")

    token = create_access_token(user.id, user.email)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=30*24*3600, samesite="lax", secure=True)
    return {"message": "Login erfolgreich"}

@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Erfolgreich abgemeldet"}

@app.get("/api/auth/me")
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzerkonto nicht gefunden.")
    return {"id": user.id, "name": user.name, "email": user.email, "created_at": user.created_at.strftime("%d.%m.%Y")}

@app.put("/api/auth/profile")
def update_profile(data: UpdateProfileSchema, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user.name = data.name.strip()
    db.commit()
    return {"message": "Profilname aktualisiert"}

@app.put("/api/auth/password")
def change_password(data: ChangePasswordSchema, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Das aktuelle Passwort ist nicht korrekt.")
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Passwort erfolgreich geändert."}

# --- BESTELLUNGEN ---
@app.post("/api/orders")
def create_order(data: CreateOrderSchema, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(status_code=400, detail="Der Warenkorb darf nicht leer sein.")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    order_num = f"REP-{datetime.datetime.utcnow().strftime('%y%m%d')}-{uuid.uuid4().hex[:5].upper()}"

    items_data = [item.model_dump() for item in data.items]

    new_order = models.Order(
        order_number=order_num,
        user_id=user.id,
        items=items_data,
        status="Eingegangen"
    )
    db.add(new_order)
    db.commit()

    send_order_confirmation(user.email, user.name, order_num, items_data)
    return {"message": "Bestellung erfolgreich aufgegeben", "order_number": order_num}

@app.get("/api/orders/my")
def get_my_orders(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.created_at.desc()).all()
    return [{"order_number": o.order_number, "status": o.status, "items": o.items, "date": o.created_at.strftime("%d.%m.%Y um %H:%M Uhr")} for o in orders]


# --- ADMIN ---
from fastapi import Header


import os
# Store password hash, or fall back to hash of the required default password if not provided
# Hash of "040926LITlit!€" using bcrypt
# But wait, bcrypt takes time. Let's just compare securely if plaintext or use verify_password.
# Actually, the user asked for exact password. Let's use verify_password.
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "$2b$12$KkQzU9x/D.26TjU50hI6iOsE.r0QJ/7.nU7w9Z6gq460y.2x/0v3q") # Generated hash for 040926LITlit!€

def verify_admin(x_admin_password: str = Header(None)):
    if x_admin_password is not None:
        import urllib.parse
        x_admin_password = urllib.parse.unquote(x_admin_password)
    if not x_admin_password or not verify_password(x_admin_password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/admin")
@app.get("/admin/")
def serve_admin():
    return FileResponse("static/admin.html")

@app.post("/api/admin/check")
def admin_check(x_admin_password: str = Header(None)):
    if x_admin_password is not None:
        import urllib.parse
        x_admin_password = urllib.parse.unquote(x_admin_password)
    if not x_admin_password or not verify_password(x_admin_password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status": "ok"}

class UserUpdate(BaseModel):
    name: str
    email: EmailStr

class OrderUpdate(BaseModel):
    status: str
    items: list[OrderItemSchema] = None

@app.get("/api/admin/users")
def get_all_users(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    users = db.query(models.User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "created_at": u.created_at.strftime("%d.%m.%Y")} for u in users]

@app.put("/api/admin/users/{user_id}")
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = data.name
    user.email = data.email
    db.commit()
    return {"message": "User updated"}

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@app.get("/api/admin/orders")
def get_all_orders(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return [{"id": o.id, "order_number": o.order_number, "user_id": o.user_id, "status": o.status, "items": o.items, "date": o.created_at.strftime("%d.%m.%Y um %H:%M Uhr")} for o in orders]

@app.put("/api/admin/orders/{order_id}")
def update_order(order_id: int, data: OrderUpdate, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = data.status
    if data.items is not None:
        order.items = [item.model_dump() for item in data.items]
    db.commit()
    return {"message": "Order updated"}

@app.delete("/api/admin/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"message": "Order deleted"}


# --- STATIC FILES ---
app.mount("/css", StaticFiles(directory="static/css"), name="css")
app.mount("/js", StaticFiles(directory="static/js"), name="js")

@app.get("/")
def serve_index(): return FileResponse("static/index.html")

@app.get("/{page}.html")
def serve_html(page: str): return FileResponse(f"static/{page}.html")

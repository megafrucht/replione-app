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

# Schemas
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
    image: str = ""
    size: str = ""
    color: str = ""
    notes: str = ""

class CreateOrderSchema(BaseModel):
    items: list[OrderItemSchema]

# ----------------- AUTH & ACCOUNT -----------------

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
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=30 * 24 * 3600,
        samesite="lax",
        secure=True
    )
    return {"message": "Registrierung erfolgreich", "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email}}

@app.post("/api/auth/login")
def login(data: LoginSchema, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Ungültige E-Mail-Adresse oder falsches Passwort.")

    token = create_access_token(user.id, user.email)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=30 * 24 * 3600,
        samesite="lax",
        secure=True
    )
    return {"message": "Login erfolgreich", "user": {"id": user.id, "name": user.name, "email": user.email}}

@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Erfolgreich abgemeldet"}

@app.get("/api/auth/me")
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzerkonto nicht gefunden.")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.strftime("%d.%m.%Y")
    }

@app.put("/api/auth/profile")
def update_profile(data: UpdateProfileSchema, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden.")
    user.name = data.name.strip()
    db.commit()
    return {"message": "Profilname erfolgreich aktualisiert", "name": user.name}

@app.put("/api/auth/password")
def change_password(data: ChangePasswordSchema, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden.")
    
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Das aktuelle Passwort ist nicht korrekt.")

    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Passwort erfolgreich geändert."}

# ----------------- BESTELLUNGEN -----------------

@app.post("/api/orders")
def create_order(data: CreateOrderSchema, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(status_code=400, detail="Der Warenkorb darf nicht leer sein.")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    order_num = f"REP-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    items_data = [item.model_dump() for item in data.items]

    new_order = models.Order(
        order_number=order_num,
        user_id=user.id,
        items=items_data,
        status="Eingegangen"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    send_order_confirmation(user.email, user.name, order_num, items_data)

    return {"message": "Bestellung erfolgreich aufgegeben", "order_number": order_num}

@app.get("/api/orders/my")
def get_my_orders(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.created_at.desc()).all()
    return [
        {
            "order_number": o.order_number,
            "status": o.status,
            "items": o.items,
            "date": o.created_at.strftime("%d.%m.%Y um %H:%M Uhr")
        }
        for o in orders
    ]

# ----------------- STATIC FILES & ROUTING -----------------
app.mount("/css", StaticFiles(directory="static/css"), name="css")
app.mount("/js", StaticFiles(directory="static/js"), name="js")

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

@app.get("/{page}.html")
def serve_html(page: str):
    return FileResponse(f"static/{page}.html")

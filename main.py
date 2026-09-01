import json
import uuid
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Response, status, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models
import auth
from email_bot import send_order_confirmation

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Replione API")

# Schemas
class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class OrderCreateSchema(BaseModel):
    items: list

# --- AUTH ENDPOINTS ---

@app.post("/api/auth/register")
def register(data: RegisterSchema, response: Response, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Diese E-Mail ist bereits registriert.")

    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Das Passwort muss mindestens 8 Zeichen lang sein.")

    new_user = models.User(
        name=data.name,
        email=data.email,
        password_hash=auth.hash_password(data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = auth.create_token(new_user.id)
    response.set_cookie(key=auth.COOKIE_NAME, value=token, httponly=True, samesite="lax", max_age=2592000)

    return {"user": {"id": new_user.id, "name": new_user.name, "email": new_user.email}}

@app.post("/api/auth/login")
def login(data: LoginSchema, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="E-Mail oder Passwort ist falsch.")

    token = auth.create_token(user.id)
    response.set_cookie(key=auth.COOKIE_NAME, value=token, httponly=True, samesite="lax", max_age=2592000)

    return {"user": {"id": user.id, "name": user.name, "email": user.email}}

@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(key=auth.COOKIE_NAME)
    return {"message": "Erfolgreich abgemeldet."}

@app.get("/api/auth/me")
def get_me(user: models.User = Depends(auth.get_current_user)):
    return {"user": {"id": user.id, "name": user.name, "email": user.email}}

# --- ORDER ENDPOINTS ---

@app.post("/api/orders")
def create_order(
    data: OrderCreateSchema, 
    background_tasks: BackgroundTasks,
    user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(get_db)
):
    if not data.items:
        raise HTTPException(status_code=400, detail="Der Warenkorb ist leer.")

    order_num = f"REP-{uuid.uuid4().hex[:8].upper()}"
    new_order = models.Order(
        order_number=order_num,
        user_id=user.id,
        items_json=json.dumps(data.items),
        status="Eingegangen"
    )
    db.add(new_order)
    db.commit()

    # E-Mail asynchron im Hintergrund absenden
    background_tasks.add_task(
        send_order_confirmation,
        to_email=user.email,
        user_name=user.name,
        order_number=order_num,
        items=data.items
    )

    return {"order_number": order_num}

@app.get("/api/orders/my")
def get_my_orders(user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(models.Order.user_id == user.id).order_by(models.Order.created_at.desc()).all()
    
    result = []
    for o in orders:
        try:
            items_list = json.loads(o.items_json)
        except:
            items_list = []
            
        result.append({
            "order_number": o.order_number,
            "created_at": o.created_at.isoformat(),
            "status": o.status,
            "items": items_list,
            "item_count": len(items_list)
        })
    return {"orders": result}

# --- STATIC FILES (Frontend) ---
app.mount("/", StaticFiles(directory="static", html=True), name="static")
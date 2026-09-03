from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database import models
from backend.schemas.auth import RegisterSchema, LoginSchema, UpdateProfileSchema, ChangePasswordSchema
from backend.core.security import hash_password, verify_password, create_access_token, get_current_user_id

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
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

@router.post("/login")
def login(data: LoginSchema, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Ungültige E-Mail-Adresse oder falsches Passwort.")

    token = create_access_token(user.id, user.email)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=30*24*3600, samesite="lax", secure=True)
    return {"message": "Login erfolgreich"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Erfolgreich abgemeldet"}

@router.get("/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzerkonto nicht gefunden.")
    return {"id": user.id, "name": user.name, "email": user.email, "created_at": user.created_at.isoformat()}

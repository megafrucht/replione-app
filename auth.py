import os
import datetime
import bcrypt
import jwt
from fastapi import Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from models import User

SECRET_KEY = os.getenv("SECRET_KEY", "replione_super_secure_jwt_secret_key_change_me")
ALGORITHM = "HS256"
COOKIE_NAME = "replione_session"

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nicht angemeldet.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ungültige Session.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Benutzer nicht gefunden.")
    return user
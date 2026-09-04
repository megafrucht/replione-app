from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import HTTPException, Request, status
from .config import settings
from .models import User
COOKIE_NAME = "replione_session"
SESSION_DAYS = 14
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )
    return hashed.decode("utf-8")
def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )
def create_session_token(
    user_id: int,
    is_admin: bool = False,
) -> str:
    if not settings.SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY ist nicht gesetzt."
        )
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "admin": is_admin,
        "iat": now,
        "exp": now + timedelta(days=SESSION_DAYS),
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256",
    )
def decode_session_token(token: str):
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
    except jwt.PyJWTError:
        return None
def set_session_cookie(response, token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_DAYS * 24 * 60 * 60,
    )
def clear_session_cookie(response):
    response.delete_cookie(
        key=COOKIE_NAME,
    )
def get_current_user(
    request: Request,
    db,
) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nicht eingeloggt.",
        )
    payload = decode_session_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sitzung ist ungültig oder abgelaufen.",
        )
    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Sitzung.",
        )
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Benutzer nicht gefunden.",
        )
    return user
def require_admin(
    request: Request,
    db,
) -> User:
    user = get_current_user(request, db)
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administratorrechte erforderlich.",
        )
    return user

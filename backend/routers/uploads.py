import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from backend.core.security import get_current_user_id, verify_admin_token
from backend.database.database import get_db
from backend.database import models
from backend.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_STORAGE_BUCKET

router = APIRouter(prefix="/api/upload", tags=["uploads"])

UPLOAD_DIR = "frontend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Supabase Client Initialization (if env vars exist)
supabase = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        print("Warning: Failed to init Supabase client", e)

@router.post("")
def upload_screenshot(request: Request, file: UploadFile = File(...)):
    user_id = get_current_user_id(request)

    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
        raise HTTPException(status_code=400, detail="Ungültiges Dateiformat. Erlaubt sind JPG, PNG, WEBP.")

    screenshot_id = f"user_{user_id}_{uuid.uuid4().hex}.{ext}"

    file_bytes = file.file.read()

    if supabase:
        try:
            res = supabase.storage.from_(SUPABASE_STORAGE_BUCKET).upload(
                file=file_bytes,
                path=screenshot_id,
                file_options={"content-type": file.content_type}
            )
            # if successful, no local saving needed for prod, but we keep it identical
        except Exception as e:
            # Fallback to local if bucket doesn't exist or error
            pass

    # Always save local as fallback for this environment
    file_path = os.path.join(UPLOAD_DIR, screenshot_id)
    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    return {"screenshot_id": screenshot_id, "url": f"/api/upload/{screenshot_id}"}

@router.get("/{screenshot_id}")
def get_screenshot(screenshot_id: str, request: Request, db: Session = Depends(get_db)):
    # 1. Verify if user is admin
    is_admin = False
    try:
        if verify_admin_token(request):
            is_admin = True
    except:
        pass

    # 2. If not admin, check if user is the owner
    if not is_admin:
        try:
            user_id = get_current_user_id(request)

            # Check cart items
            in_cart = db.query(models.CartItem).filter(
                models.CartItem.screenshot_id == screenshot_id,
                models.CartItem.user_id == user_id
            ).first()

            # Check order items
            in_order = db.query(models.OrderItem).join(models.Order).filter(
                models.OrderItem.screenshot_id == screenshot_id,
                models.Order.user_id == user_id
            ).first()

            if not in_cart and not in_order:
                raise HTTPException(status_code=403, detail="Kein Zugriff auf diesen Screenshot")
        except Exception as e:
            raise HTTPException(status_code=403, detail="Kein Zugriff auf diesen Screenshot")

    # Serve the file (local fallback or download from supabase)
    # Since we saved it locally as fallback, we serve the local file for simplicity
    file_path = os.path.join(UPLOAD_DIR, screenshot_id)
    if os.path.exists(file_path):
        return FileResponse(file_path)

    if supabase:
        try:
            res = supabase.storage.from_(SUPABASE_STORAGE_BUCKET).download(screenshot_id)
            return Response(content=res, media_type="image/*")
        except Exception as e:
            pass

    raise HTTPException(status_code=404, detail="Screenshot nicht gefunden")

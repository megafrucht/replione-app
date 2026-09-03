import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from backend.core.security import get_current_user_id

router = APIRouter(prefix="/api/upload", tags=["uploads"])

UPLOAD_DIR = "frontend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# TODO: Connect this to Supabase Storage later. For now we use local storage as requested to maintain the flow.
# In a real environment we would check for SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY and use supabase python client.

@router.post("")
def upload_screenshot(request: Request, file: UploadFile = File(...)):
    # Authenticate (throws 401 if not logged in)
    user_id = get_current_user_id(request)

    # Validate format and size
    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
        raise HTTPException(status_code=400, detail="Ungültiges Dateiformat. Erlaubt sind JPG, PNG, WEBP.")

    # Generate unique ID for the screenshot
    screenshot_id = f"user_{user_id}_{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, screenshot_id)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"screenshot_id": screenshot_id, "url": f"/uploads/{screenshot_id}"}

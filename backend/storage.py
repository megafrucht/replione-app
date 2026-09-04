import io
import uuid
from fastapi import HTTPException, UploadFile
from PIL import Image
from supabase import create_client
from .config import settings
ALLOWED_MIME_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MAX_FILE_SIZE = 8 * 1024 * 1024
def get_supabase():
    if not settings.SUPABASE_URL:
        raise RuntimeError(
            "SUPABASE_URL ist nicht gesetzt."
        )
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "SUPABASE_SERVICE_ROLE_KEY ist nicht gesetzt."
        )
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )
async def upload_screenshot(
    upload: UploadFile,
    user_id: int,
) -> str:
    if upload.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Nur JPG, PNG und WebP sind erlaubt.",
        )
    data = await upload.read()
    if not data:
        raise HTTPException(
            status_code=400,
            detail="Die Datei ist leer.",
        )
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Das Bild darf maximal 8 MB groß sein.",
        )
    try:
        image = Image.open(io.BytesIO(data))
        image.verify()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Die Datei ist kein gültiges Bild.",
        )
    extension = ALLOWED_MIME_TYPES[upload.content_type]
    filename = f"{uuid.uuid4().hex}.{extension}"
    path = f"users/{user_id}/{filename}"
    supabase = get_supabase()
    import logging
    try:
        supabase.storage.from_(
            settings.SUPABASE_STORAGE_BUCKET
        ).upload(
            path,
            data,
            {
                "content-type": upload.content_type,
                "upsert": "false",
            },
        )
    except Exception as exc:
        logging.exception(f"Supabase Storage Upload Error for path {path}:")
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Hochladen des Screenshots.",
        )
    return path
def download_screenshot(path: str) -> bytes:
    supabase = get_supabase()
    try:
        return supabase.storage.from_(
            settings.SUPABASE_STORAGE_BUCKET
        ).download(path)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Screenshot nicht gefunden.",
        )
def delete_screenshot(path: str):
    if not path:
        return
    try:
        supabase = get_supabase()
        supabase.storage.from_(
            settings.SUPABASE_STORAGE_BUCKET
        ).remove([path])
    except Exception:
        pass

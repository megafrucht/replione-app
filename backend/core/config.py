import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./replione.db").strip()
SECRET_KEY = os.getenv("SECRET_KEY", "replione_super_secure_jwt_token_key_2026_xyz")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "040926LITlit!€")

# E-Mail Settings
SMTP_HOST = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "bestellung@replione.de")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")

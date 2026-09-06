import os
from dotenv import load_dotenv
load_dotenv()
class Settings:
    APP_NAME = "Replione"
    APP_VERSION = "1.0.0"
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv(
        "SUPABASE_SERVICE_ROLE_KEY"
    )
    SUPABASE_STORAGE_BUCKET = os.getenv(
        "SUPABASE_STORAGE_BUCKET",
        "order-screenshots",
    )
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    def validate(self):
        required = {
            "DATABASE_URL": self.DATABASE_URL,
            "SECRET_KEY": self.SECRET_KEY,
            "ADMIN_PASSWORD": self.ADMIN_PASSWORD,
            "SUPABASE_URL": self.SUPABASE_URL,
            "SUPABASE_SERVICE_ROLE_KEY": self.SUPABASE_SERVICE_ROLE_KEY,
            "SMTP_HOST": self.SMTP_HOST,
            "SMTP_USER": self.SMTP_USER,
            "SMTP_PASSWORD": self.SMTP_PASSWORD,
            "SENDER_EMAIL": self.SENDER_EMAIL,
        }
        missing = [
            name
            for name, value in required.items()
            if not value
        ]
        if missing:
            raise RuntimeError(
                "Folgende Environment Variables fehlen: "
                + ", ".join(missing)
            )
settings = Settings()

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Standardmäßig lokale SQLite, falls keine Supabase-URL gesetzt ist
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./replione.db").strip()

# WICHTIG: SQLAlchemy braucht 'postgresql://' statt 'postgres://' für Supabase
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

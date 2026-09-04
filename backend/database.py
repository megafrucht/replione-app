from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings
class Base(DeclarativeBase):
    pass
def create_database_engine():
    if not settings.DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL ist nicht gesetzt."
        )
    return create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
    )
engine = create_database_engine()
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

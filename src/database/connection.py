from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from src.config.settings import get_settings
from loguru import logger

settings = get_settings()
 
# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
)
 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
@contextmanager
def get_db() -> Session:
    """
    Database session context manager
    
    Usage:
        with get_db() as db:
            product = ProductCRUD.get_product(db, product_id=1)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()
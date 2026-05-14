"""
Database Session Management

Configures SQLAlchemy engine, session factory, and database initialization.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.config import settings

# Create database engine
# NullPool is used for better compatibility in test and serverless environments.
engine_kwargs = {
    "echo": settings.db_echo,
    "pool_pre_ping": True,
}

if settings.environment == "testing":
    engine_kwargs["poolclass"] = NullPool

if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    **engine_kwargs,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """
    Dependency for getting database session in FastAPI routes.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    Note: In production, use Alembic migrations instead.
    """
    from app.database.models import Base
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all tables (for testing purposes).
    
    WARNING: This deletes all data. Use only in testing!
    """
    from app.database.models import Base
    Base.metadata.drop_all(bind=engine)

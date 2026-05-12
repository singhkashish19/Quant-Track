"""
Database Session Management

Configures SQLAlchemy engine, session factory, and database initialization.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.config import settings

# Create database engine
# NullPool is used for better compatibility in certain environments
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    poolclass=NullPool if settings.environment == "testing" else None,
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

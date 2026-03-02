"""
SQLAlchemy database configuration and session management.

This module provides:
- Database engine setup
- Session factory
- SQLAlchemy Base for ORM models
- Dependency injection for FastAPI
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator

# Get database URL from environment or use default PostgreSQL URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/penumbra"
)

# Check if we should enable SQL echo (debug logging)
SQL_DEBUG = os.getenv("SQL_DEBUG", "false").lower() == "true"

# Create database engine
engine = create_engine(
    DATABASE_URL,
    echo=SQL_DEBUG,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base for ORM models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency injection function for FastAPI.
    
    Yields a database session for each request.
    Usage in FastAPI:
        @app.get("/some_endpoint")
        def some_endpoint(db: Session = Depends(get_db)):
            ...
    
    Yields:
        Session: SQLAlchemy session instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    
    Should be called once at application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all tables from the database.
    
    Use with caution - this deletes all data!
    """
    Base.metadata.drop_all(bind=engine)

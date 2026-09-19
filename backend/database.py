"""
Database setup for the AI Customer Support Agent.

Uses SQLAlchemy with a local SQLite file (support.db). On import, the engine
and session factory are created. Call init_db() once at application startup
to create tables and seed sample data if the database is empty.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "support.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False is required because FastAPI can access the
# connection from different threads within a single request lifecycle.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (if they don't exist) and seed sample orders."""
    # Import models here so they're registered on Base before create_all runs.
    import models  # noqa: F401
    from sqlalchemy.orm import Session

    Base.metadata.create_all(bind=engine)

    # Seed sample orders only if the orders table is empty.
    db: Session = SessionLocal()
    try:
        from models import Order

        if db.query(Order).count() == 0:
            from seed import seed_orders

            seed_orders(db)
    finally:
        db.close()

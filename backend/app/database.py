import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# A single local file. Delete lost_and_found.db any time to start fresh.
DATABASE_URL = os.environ("POSTGRES_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """Give each request its own database session, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

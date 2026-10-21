import logging
import os
from pathlib import Path
import time

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError


# A single local file. Delete lost_and_found.db any time to start fresh.
DATABASE_URL = os.environ["POSTGRES_URL"]
ATTEMPTS = 5
for i in range(ATTEMPTS):
    try:
        engine = create_engine(DATABASE_URL, connect_args={"passfile": os.environ["PGPASSFILE"]})
        connection_success = True
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        break
    except OperationalError as e:
        if i == ATTEMPTS - 1:
            raise e
        time.sleep(5)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) # type: ignore
Base = declarative_base()


def get_db():
    """Give each request its own database session, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

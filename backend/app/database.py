import logging
import os
from pathlib import Path
import time

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase, MappedAsDataclass
from sqlalchemy.exc import OperationalError

# Database might start later than it creates the engine
DATABASE_URL = os.environ["POSTGRES_URL"]
ATTEMPTS = 5
for i in range(ATTEMPTS):
    try:
        logging.info("PASSFILE: %s", os.environ["PGPASSFILE"])
        engine = create_engine(DATABASE_URL, connect_args={"passfile": os.environ["PGPASSFILE"]})
        connection_success = True
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        break
    except OperationalError as e:
        if i == ATTEMPTS - 1:
            raise e
        time.sleep(1)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) # type: ignore
class Base(MappedAsDataclass, DeclarativeBase):
    pass

def get_db():
    """Give each request its own database session, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

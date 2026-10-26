import logging
import os
import time
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    declarative_base,
    sessionmaker,
)

# Database might start later than it creates the engine
DATABASE_URL = os.environ.get("POSTGRES_URL", "postgresql+psycopg2://main@127.0.0.1:5433/lafs")
PGPASSFILE = os.environ.get("PGPASSFILE", (Path(__file__).parent.parent.parent / "secrets/.pgpass").as_posix())
ATTEMPTS = 8
for i in range(ATTEMPTS):
    try:
        logging.info("PASSFILE: %s, exist=%s", PGPASSFILE, Path(PGPASSFILE).exists()) 
        engine = create_engine(DATABASE_URL, connect_args={"passfile": PGPASSFILE})
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

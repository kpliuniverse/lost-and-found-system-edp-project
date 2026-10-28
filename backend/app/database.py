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

from app.database_url import normalize_postgres_url

# Database might start later than it creates the engine
DATABASE_URL = normalize_postgres_url(
    os.environ.get("POSTGRES_URL", "postgresql+psycopg2://main@127.0.0.1:5433/lafs")
)
PGPASSFILE = os.environ.get("PGPASSFILE")
if PGPASSFILE is None:
    default_passfile = Path(__file__).parent.parent.parent / "secrets/.pgpass"
    if default_passfile.is_file():
        PGPASSFILE = default_passfile.as_posix()
CONNECT_ARGS = {"passfile": PGPASSFILE} if PGPASSFILE else {}
ATTEMPTS = 8
engine = None
for i in range(ATTEMPTS):
    try:
        if PGPASSFILE:
            logging.info("PASSFILE: %s, exist=%s", PGPASSFILE, Path(PGPASSFILE).exists())
        engine = create_engine(DATABASE_URL, connect_args=CONNECT_ARGS)
        connection_success = True
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        break
    except OperationalError as e:
        if i == ATTEMPTS - 1:
            raise e
        time.sleep(1)
assert engine is not None

def get_db():
    """Give each request its own database session, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

class Base(MappedAsDataclass, DeclarativeBase):
    pass

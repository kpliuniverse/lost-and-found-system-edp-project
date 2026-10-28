from sqlalchemy.engine import make_url


def normalize_postgres_url(database_url: str) -> str:
    url = make_url(database_url)
    if url.drivername == "postgresql+psycopg":
        return url.set(drivername="postgresql+psycopg2").render_as_string(
            hide_password=False
        )
    return database_url

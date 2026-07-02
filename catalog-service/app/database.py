from collections.abc import AsyncGenerator
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


odbc_connection_string = (
    f"DRIVER={{{settings.db_driver}}};"
    f"SERVER={settings.db_server};"
    f"DATABASE={settings.db_name};"
    f"UID={settings.db_user};"
    f"PWD={settings.db_password};"
    f"Encrypt={'yes' if settings.db_encrypt else 'no'};"
    f"TrustServerCertificate="
    f"{'yes' if settings.db_trust_server_certificate else 'no'};"
)


ASYNC_DATABASE_URL = URL.create(
    "mssql+aioodbc",
    query={
        "odbc_connect": odbc_connection_string,
    },
)


SYNC_DATABASE_URL = URL.create(
    "mssql+pyodbc",
    query={
        "odbc_connect": odbc_connection_string,
    },
)


engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
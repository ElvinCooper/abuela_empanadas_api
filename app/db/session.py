from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

database_url = settings.DATABASE_URL
if not database_url:
    database_url = "postgresql+asyncpg://localhost:5432/postgres"
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Remover parámetros que asyncpg no soporta (ej. sslmode)
if "sslmode=" in database_url:
    parsed = urlparse(database_url)
    query_params = parse_qs(parsed.query)
    if "sslmode" in query_params:
        del query_params["sslmode"]
    new_query = urlencode(query_params, doseq=True)
    database_url = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        )
    )

async_engine = create_async_engine(database_url)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass

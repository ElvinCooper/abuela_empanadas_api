import os
import pytest
import pytest_asyncio
import sqlalchemy as sa
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from uuid import uuid4
from app.main import app
from app.core.dependencies import get_db
from app.db.session import Base
from app.core.config import settings


def build_test_database_url(database_url: str, derive_database_name: bool) -> str:
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    database_url = database_url.replace("-pooler.", ".")

    parsed = urlparse(database_url)
    database_name = parsed.path.lstrip("/")
    if derive_database_name:
        database_name = (
            database_name.replace("abuela_empanadas", "abuela_empanadas_test")
            if "abuela_empanadas" in database_name
            else f"{database_name}_test"
        )
    query_params = parse_qs(parsed.query)
    query_params.pop("sslmode", None)
    query_params.pop("channel_binding", None)
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            f"/{database_name}",
            parsed.params,
            urlencode(query_params, doseq=True),
            parsed.fragment,
        )
    )


pg_user = os.getenv("TEST_POSTGRES_USER")
pg_pass = os.getenv("TEST_POSTGRES_PASSWORD")
pg_db = os.getenv("TEST_POSTGRES_DB")
if pg_user and pg_pass and pg_db:
    configured_test_database_url = (
        f"postgresql://{pg_user}:{pg_pass}@127.0.0.1:5433/{pg_db}"
    )
else:
    configured_test_database_url = (
        os.getenv("TEST_DATABASE_URL") or settings.TEST_DATABASE_URL
    )
if configured_test_database_url:
    TEST_DATABASE_URL = build_test_database_url(
        configured_test_database_url,
        derive_database_name=False,
    )
else:
    TEST_DATABASE_URL = build_test_database_url(
        settings.DATABASE_URL,
        derive_database_name=True,
    )


@pytest_asyncio.fixture(scope="module")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        connect_args={
            "prepared_statement_cache_size": 0,
            "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
        },
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        from app.models.sucursal import Sucursal
        from app.models.status_factura import StatusFactura
        from app.models.moneda import Moneda
        from app.models.metodo_pago import MetodoPago
        from app.models.producto import Producto

        await conn.execute(
            Moneda.__table__.insert(),
            [
                {
                    "id": 1,
                    "nombre": "Peso Dominicano",
                    "simbolo": "RD$",
                    "activo": True,
                },
                {"id": 2, "nombre": "Dólar", "simbolo": "$", "activo": True},
            ],
        )
        await conn.execute(
            MetodoPago.__table__.insert(),
            [
                {"id": 1, "nombre": "Efectivo", "activo": True},
                {"id": 2, "nombre": "Tarjeta", "activo": True},
                {"id": 3, "nombre": "Transferencia", "activo": True},
            ],
        )
        await conn.execute(
            StatusFactura.__table__.insert(),
            [
                {
                    "id": 1,
                    "nombre": "pendiente",
                    "descripcion": "Factura pendiente de pago",
                    "activo": True,
                },
                {
                    "id": 2,
                    "nombre": "pagada",
                    "descripcion": "Factura pagada",
                    "activo": True,
                },
                {
                    "id": 3,
                    "nombre": "anulada",
                    "descripcion": "Factura anulada",
                    "activo": True,
                },
            ],
        )
        await conn.execute(
            Sucursal.__table__.insert(),
            [
                {
                    "id": 1,
                    "nombre": "Sucursal Principal",
                    "direccion": "Principal",
                    "telefono": "0000",
                    "activo": True,
                }
            ],
        )
        await conn.execute(
            sa.text(
                "SELECT setval('sucursales_id_seq', (SELECT MAX(id) FROM sucursales))"
            )
        )
        await conn.execute(
            Producto.__table__.insert(),
            [
                {
                    "id": 1,
                    "sucursal_id": 1,
                    "nombre": "Empanada de carne",
                    "descripcion": "Rellena de carne",
                    "precio": 100,
                    "stock": 100,
                    "activo": True,
                },
                {
                    "id": 2,
                    "sucursal_id": 1,
                    "nombre": "Empanada de pollo",
                    "descripcion": "Rellena de pollo",
                    "precio": 120,
                    "stock": 100,
                    "activo": True,
                },
            ],
        )
        await conn.execute(
            sa.text(
                "SELECT setval('productos_id_seq', (SELECT MAX(id) FROM productos))"
            )
        )
    yield
    async with test_engine.begin() as conn:
        await conn.execute(
            sa.text(
                """
                TRUNCATE TABLE
                    anulaciones,
                    factura_detalles,
                    facturas,
                    cierres_diarios,
                    egresos,
                    stocks,
                    productos,
                    insumos,
                    usuarios,
                    sucursales,
                    proveedores,
                    status_factura,
                    monedas,
                    metodo_pago
                RESTART IDENTITY CASCADE
                """
            )
        )


@pytest_asyncio.fixture(scope="module")
async def db_session(test_engine, setup_database):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="module")
async def async_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="module")
async def usuario_admin(db_session):
    from app.models.usuario import Usuario, RolEnum
    from app.core.security import create_access_token, hash_password

    result = await db_session.execute(
        sa.select(Usuario).where(Usuario.username == "admin")
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = Usuario(
            sucursal_id=1,
            nombre="Admin",
            username="admin",
            password_hash=hash_password("admin123"),
            rol=RolEnum.admin,
            activo=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
    user.token = create_access_token({"sub": str(user.id), "rol": user.rol})
    return user

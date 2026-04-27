import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base
from app.core.config import settings

TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "abuela_empanadas", "abuela_empanadas_test"
)


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_engine, setup_database):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def usuario_admin(db_session):
    from app.models.usuario import Usuario, RolEnum
    from app.core.security import hash_password

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
    return user

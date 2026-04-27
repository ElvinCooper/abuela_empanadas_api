from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.factura import FacturaCreate


async def create_factura(db: AsyncSession, factura: FacturaCreate) -> None:
    raise NotImplementedError

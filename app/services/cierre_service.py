from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.cierre import CierreDiarioCreate


async def create_cierre(db: AsyncSession, cierre: CierreDiarioCreate) -> None:
    raise NotImplementedError

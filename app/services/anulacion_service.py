from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.anulacion import AnulacionCreate


async def create_anulacion(db: AsyncSession, anulacion: AnulacionCreate) -> None:
    raise NotImplementedError

from app.schemas.common import BaseSchema


class AnulacionCreate(BaseSchema):
    motivo: str


class AnulacionRead(BaseSchema):
    id: int
    factura_id: int
    motivo: str

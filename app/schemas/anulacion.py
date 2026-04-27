from app.schemas.common import BaseSchema


class AnulacionCreate(BaseSchema):
    factura_id: int
    motivo: str


class AnulacionRead(BaseSchema):
    id: int
    factura_id: int
    motivo: str

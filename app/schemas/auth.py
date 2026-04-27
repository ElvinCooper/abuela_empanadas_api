from app.schemas.usuario import UsuarioRead


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioRead

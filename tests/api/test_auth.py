import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["usuario"]["username"] == "admin"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


@pytest.mark.asyncio
async def test_login_wrong_username(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "noexiste", "password": "admin123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_read_me(async_client, usuario_admin):
    headers = {"Authorization": f"Bearer {usuario_admin.token}"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "admin"
    assert body["id"] == usuario_admin.id


@pytest.mark.asyncio
async def test_read_me_unauthorized(async_client, usuario_admin):
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(async_client, usuario_admin):
    headers = {"Authorization": f"Bearer {usuario_admin.token}"}
    response = await async_client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 204

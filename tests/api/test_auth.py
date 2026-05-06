import pytest


@pytest.mark.asyncio
async def test_login(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

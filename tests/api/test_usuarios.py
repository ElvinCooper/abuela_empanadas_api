import pytest


@pytest.mark.asyncio
async def test_list_usuarios_with_admin(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/usuarios/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_usuario_with_admin(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/usuarios/",
        json={
            "sucursal_id": 1,
            "nombre": "Juan",
            "username": "juan_test",
            "password": "juan123",
            "rol": "standard",
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Juan"
    assert data["username"] == "juan_test"
    assert data["rol"] == "standard"


@pytest.mark.asyncio
async def test_create_usuario_forbidden_for_standard(async_client, usuario_standard):
    response = await async_client.post(
        "/api/v1/usuarios/",
        json={
            "sucursal_id": 1,
            "nombre": "Otro",
            "username": "otro_user",
            "password": "otro123",
            "rol": "standard",
        },
        headers={"Authorization": f"Bearer {usuario_standard.token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"

import pytest


@pytest.mark.asyncio
async def test_list_sucursales(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/sucursales/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_sucursal_with_valid_data(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/sucursales/",
        json={
            "nombre": "Centro",
            "direccion": "Av 1 #123",
            "telefono": "555-1234",
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Centro"
    assert data["direccion"] == "Av 1 #123"
    assert data["activo"] is True

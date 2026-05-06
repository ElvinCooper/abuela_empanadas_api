import pytest


@pytest.mark.asyncio
async def test_list_productos(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/productos/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_producto_with_valid_data(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/productos/",
        json={
            "sucursal_id": 1,
            "nombre": "Empanada de carne",
            "descripcion": "Rellena de carne",
            "precio": 1,
            "stock": 100,
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Empanada de carne"
    assert data["sucursal_id"] == 1
    assert data["activo"] is True

import pytest


@pytest.mark.asyncio
async def test_list_insumos(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/insumos/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_insumo_with_valid_data(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/insumos/",
        json={
            "sucursal_id": 1,
            "proveedor_id": None,
            "nombre": "Harina",
            "stock": 50,
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Harina"
    assert data["stock"] == 50
    assert data["activo"] is True

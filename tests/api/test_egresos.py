import pytest


@pytest.mark.asyncio
async def test_list_gastos(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/gastos/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_gasto_with_valid_data(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/gastos/",
        json={
            "sucursal_id": 1,
            "descripcion": "Compra insumos",
            "monto": 75,
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["descripcion"] == "Compra insumos"
    assert data["monto"] == 75

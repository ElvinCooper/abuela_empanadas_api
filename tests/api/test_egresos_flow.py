import pytest

_egreso_id: int | None = None


@pytest.mark.asyncio
async def test_list_gastos_empty(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/gastos/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_gasto(async_client, usuario_admin):
    global _egreso_id
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
    assert data["sucursal_id"] == 1
    assert data["sucursal_nombre"] == "Sucursal Principal"
    assert "id" in data
    _egreso_id = data["id"]


@pytest.mark.asyncio
async def test_list_gastos_after_create(async_client, usuario_admin):
    global _egreso_id
    assert _egreso_id is not None
    response = await async_client.get(
        "/api/v1/gastos/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    ids = [g["id"] for g in data]
    assert _egreso_id in ids


@pytest.mark.asyncio
async def test_create_gasto_invalid(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/gastos/",
        json={"descripcion": "sin sucursal"},
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_gasto_unauthorized(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/gastos/",
        json={"sucursal_id": 1, "descripcion": "test", "monto": 10},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_gastos_unauthorized(async_client, usuario_admin):
    response = await async_client.get("/api/v1/gastos/")
    assert response.status_code == 401

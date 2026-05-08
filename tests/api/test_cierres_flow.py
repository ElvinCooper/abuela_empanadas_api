import pytest

_cierre_id: int | None = None


@pytest.mark.asyncio
async def test_list_cierres_empty(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/cierres/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_cierre(async_client, usuario_admin):
    global _cierre_id
    response = await async_client.post(
        "/api/v1/cierres/",
        json={
            "sucursal_id": 1,
            "fecha": "2026-04-27",
            "total_ventas": 5000,
            "total_egresos": 1000,
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["sucursal_id"] == 1
    assert data["sucursal_nombre"] == "Sucursal Principal"
    assert data["total_ventas"] == 5000
    assert data["total_egresos"] == 1000
    assert "id" in data
    _cierre_id = data["id"]


@pytest.mark.asyncio
async def test_list_cierres_after_create(async_client, usuario_admin):
    global _cierre_id
    assert _cierre_id is not None
    response = await async_client.get(
        "/api/v1/cierres/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    ids = [c["id"] for c in data]
    assert _cierre_id in ids


@pytest.mark.asyncio
async def test_create_cierre_invalid(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/cierres/",
        json={"sucursal_id": 1},
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_cierre_unauthorized(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/cierres/",
        json={
            "sucursal_id": 1,
            "fecha": "2026-04-27",
            "total_ventas": 5000,
            "total_egresos": 1000,
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_cierres_unauthorized(async_client, usuario_admin):
    response = await async_client.get("/api/v1/cierres/")
    assert response.status_code == 401

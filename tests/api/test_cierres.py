import pytest


@pytest.mark.asyncio
async def test_create_cierre(async_client, usuario_admin):
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

import pytest


@pytest.mark.asyncio
async def test_create_factura(async_client, usuario_admin):
    response = await async_client.post(
        "/v1/facturas/",
        json={
            "sucursal_id": 1,
            "usuario_id": usuario_admin.id,
            "total": 1000,
            "pagada": False,
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201

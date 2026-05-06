import pytest


@pytest.mark.asyncio
async def test_list_proveedores(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/proveedores/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_proveedor_with_valid_data(async_client, usuario_admin):
    response = await async_client.post(
        "/api/v1/proveedores/",
        json={
            "nombre": "Proveedor A",
            "contacto": "Ana",
            "telefono": "555-0000",
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Proveedor A"
    assert data["contacto"] == "Ana"
    assert data["activo"] is True

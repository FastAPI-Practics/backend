import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.rbac import INITIAL_PERMISSION_SCHEMA
from app.models.roles import Role, RolePublic


@pytest.mark.asyncio
async def test_roles_list(async_client: AsyncClient, admin_access_token: str):
    resp = await async_client.get(
        url='/roles/',
        headers={
            'Authorization': f'Bearer {admin_access_token}',
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    items = data['items']
    roles = [RolePublic.model_validate(item) for item in items]

    assert len(roles) == len(INITIAL_PERMISSION_SCHEMA.keys())


@pytest.mark.asyncio
async def test_role_create(
    async_client: AsyncClient, admin_access_token: str, async_db: AsyncSession
):
    role_name = 'test'
    create_resp = await async_client.post(
        url='/roles/',
        headers={
            'Authorization': f'Bearer {admin_access_token}',
        },
        json={'name': role_name, 'scope_aliases': []},
    )

    assert create_resp.status_code == status.HTTP_200_OK
    data = create_resp.json()

    role = RolePublic.model_validate(data)

    assert role.name == role_name

    list_resp = await async_client.get(
        url='/roles/',
        headers={
            'Authorization': f'Bearer {admin_access_token}',
        },
    )
    assert list_resp.status_code == status.HTTP_200_OK
    data = list_resp.json()
    items = data['items']
    roles = [RolePublic.model_validate(item) for item in items]

    assert len(roles) == len(INITIAL_PERMISSION_SCHEMA.keys()) + 1

    role_from_db = await async_db.get(Role, role.id)
    await async_db.delete(role_from_db)
    await async_db.commit()

    list_resp = await async_client.get(
        url='/roles/',
        headers={
            'Authorization': f'Bearer {admin_access_token}',
        },
    )
    assert list_resp.status_code == status.HTTP_200_OK
    data = list_resp.json()
    items = data['items']
    roles = [RolePublic.model_validate(item) for item in items]

    assert len(roles) == len(INITIAL_PERMISSION_SCHEMA.keys())

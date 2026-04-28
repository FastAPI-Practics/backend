import pytest
from httpx import AsyncClient
from app.core.errors import ForbiddenError
from app.models.users import UserPublic
from app.models.roles import Role
from app.core.rbac import INITIAL_PERMISSION_SCHEMA


@pytest.mark.asyncio
async def test_public_route_content(
    async_client: AsyncClient,
    public_access_token: str
):
    resp = await async_client.get(
        url='/users/me',
        headers={
            'Authorization': f'Bearer {public_access_token}'
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    user = UserPublic.model_validate(data)

    assert user is not None
    assert user.username == 'public-user'


@pytest.mark.asyncio
async def test_roles_route_content(
    async_client: AsyncClient,
    admin_access_token: str
):
    resp = await async_client.get(
        url='/roles/',
        headers={
            'Authorization': f'Bearer {admin_access_token}'
        }
    )
    assert resp.status_code == 200

    data = resp.json()
    roles_items = data.get('items')
    roles = [Role.model_validate(role_item) for role_item in roles_items]

    assert len(roles) == len(INITIAL_PERMISSION_SCHEMA.keys())

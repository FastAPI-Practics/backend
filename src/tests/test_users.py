import pytest
from httpx import AsyncClient

from app.models.users import UserPublic


@pytest.mark.asyncio
async def test_profile(async_client: AsyncClient, admin_access_token: str):
    resp = await async_client.get(
        url='/users/me',
        headers={
            'Authorization': f'Bearer {admin_access_token}',
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    user = UserPublic.model_validate(data)

    assert user.username == 'admin'

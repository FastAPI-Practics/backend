import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.users import UserPublic


@pytest.mark.asyncio
async def test_profile(async_client: AsyncClient, admin_access_token: str):
    resp = await async_client.get(
        url='/users/me',
        headers={
            'Authorization': f'Bearer {admin_access_token}',
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    user = UserPublic.model_validate(data)

    assert user.username == 'admin'

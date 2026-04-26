import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.errors import ForbiddenError


@pytest.mark.asyncio
async def test_public_access(
    async_client: AsyncClient,
    public_access_token: str,
):
    resp = await async_client.get(
        url='/users/me',
        headers={
            'Authorization': f'Bearer {public_access_token}',
        },
    )
    assert resp.status_code == status.HTTP_200_OK


test_urls = ['/users/', '/roles/', '/pets/']


@pytest.mark.parametrize('url', test_urls)
@pytest.mark.asyncio
async def test_public_forbidden(
    async_client: AsyncClient, public_access_token: str, url: str, subtests
):
    with (
        subtests.test(msg=f'Should forbidden for {url} url'),
        pytest.raises(ForbiddenError),
    ):
        await async_client.get(
            url=url,
            headers={
                'Authorization': f'Bearer {public_access_token}',
            },
        )

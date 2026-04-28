import pytest
from httpx import AsyncClient
from app.core.errors import ForbiddenError

@pytest.mark.asyncio
async def test_public_route(
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

test_urls = [
    "/users/list",
    "/users/pets"
]

@pytest.mark.parametrize('url', test_urls)
@pytest.mark.asyncio
async def test_auth_route(
    url: str,
    async_client: AsyncClient,
    public_access_token: str,
    subtests
):
    with subtests.test(message="Testing for {url}"), pytest.raises(ForbiddenError):
        await async_client.get(
            url=url,
            headers={
                'Authorization': f'Bearer {public_access_token}'
            }
        )

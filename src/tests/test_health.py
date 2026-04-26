import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(async_client: AsyncClient):
    resp = await async_client.get('/health')
    data = resp.json()
    assert data == {'status': 'healthy'}

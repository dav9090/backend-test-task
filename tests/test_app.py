import pytest
from httpx import AsyncClient
from fastapi import status



@pytest.mark.asyncio
async def test_hello_world(client: AsyncClient) -> None:
    response = await client.get("/hello")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World"}

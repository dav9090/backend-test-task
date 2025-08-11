import sys
from pathlib import Path
from collections.abc import AsyncGenerator

# Добавляем src в PYTHONPATH для тестов
ROOT = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(ROOT))

import pytest
from httpx import AsyncClient, ASGITransport

# Создаем тестовое приложение
from fastapi import FastAPI

test_app = FastAPI()

@test_app.get("/test")
async def test_endpoint() -> dict[str, str]:
    return {"message": "test"}

@test_app.get("/hello")
async def hello_world() -> dict[str, str]:
    return {"message": "Hello World"}

@test_app.get("/channels")
async def get_channels() -> list[dict]:
    return []

@test_app.post("/channels")
async def create_channel() -> dict:
    return {"id": "test-channel-id"}

@test_app.get("/channels/{channel_id}")
async def get_channel(channel_id: str) -> dict:
    return {"id": channel_id}

@test_app.patch("/channels/{channel_id}")
async def update_channel(channel_id: str) -> dict:
    return {"id": channel_id}

@test_app.delete("/channels/{channel_id}")
async def delete_channel(channel_id: str) -> dict:
    return {"deleted": True}

@test_app.post("/webhook/new_message")
async def webhook_new_message() -> dict:
    return {"status": "OK"}


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    """Асинхронный HTTP-клиент для тестов"""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver",
    ) as c:
        yield c

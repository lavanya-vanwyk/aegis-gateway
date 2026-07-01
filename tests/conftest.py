import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import AsyncMock
from app.core.database import redis_manager


@pytest.fixture(scope="module", autouse=True)
def mock_redis():
    """
    Automatically mocks the Redis connection for all tests.
    """
    mock_client = AsyncMock()

    original_client = redis_manager.client
    redis_manager.client = mock_client

    yield mock_client

    redis_manager.client = original_client


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

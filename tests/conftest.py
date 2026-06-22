import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    ''''creates a reusable TestClient'''
    with TestClient(app) as c:
        yield c
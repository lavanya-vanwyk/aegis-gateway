import pytest
from unittest.mock import patch, AsyncMock


def test_health_check(client):
    """
    GIVEN the health check endpoint
    WHEN a GET request is made
    THEN it should return a 200 status and correct environment
    """
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "redis_connected" in data


@patch("app.api.endpoints.llm_service.generate_response", new_callable=AsyncMock)
def test_process_secure_prompt_success(mock_generate_response, client):
    """
    GIVEN a valid PromptRequest payload
    WHEN a POST request is made to /v1/privacy/chat with a valid API key
    THEN it should return a 200 status and have PromptResponse schema
    """

    mock_generate_response.return_value = (
        "System received safe prompt: Hello, <PERSON_abc123>."
    )
    payload = {"prompt": "Hello, my name is Alice.", "user_id": "usr_test_123"}
    headers = {"X-API-Key": "fake_api_key"}
    response = client.post("/v1/privacy/chat", json=payload, headers=headers)
    assert response.status_code == 200
    mock_generate_response.assert_called_once()


@pytest.mark.parametrize(
    "invalid_payload, expected_status",
    [
        ({"user_id": "usr_123"}, 422),
        ({"prompt": "Hello"}, 422),
        ({"prompt": "", "user_id": "usr_123"}, 422),  # invalid prompt length
        ({"prompt": "A" * 5001, "user_id": "usr_123"}, 422),  # invalid prompt length
    ],
)
def test_process_secure_prompt_validation_failures(
    client, invalid_payload, expected_status
):
    """
    GIVEN invalid payloads
    WHEN a POST request is made to /v1/privacy/chat with a valid API key
    THEN the gateway should automatically reject it with a 422 status
    """

    headers = {"X-API-Key": "fake_api_key"}
    response = client.post("/v1/privacy/chat", json=invalid_payload, headers=headers)

    assert response.status_code == expected_status

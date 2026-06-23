import pytest

def test_health_check(client):
    """
    GIVEN the health check endpoint
    WHEN a GET request is made
    THEN it should return a 200 status and correct environment
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "environment": "dev"}


def test_process_secure_prompt_success(client):
    """
    GIVEN a valid PromptRequest payload
    WHEN a POST request is made to /v1/privacy/chat
    THEN it should return a 200 status and have PromptResponse schema
    """
    payload = {
        "prompt": "Hello, my name is Alice.",
        "user_id": "usr_test_123"
    }
    response = client.post("/v1/privacy/chat", json=payload)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "processed_response" in data
    assert data["entities_masked_count"] == 1
    assert "timestamp" in data


@pytest.mark.parametrize(
    "invalid_payload, expected_status",
    [
        ({"user_id": "usr_123"}, 422), 
        ({"prompt": "Hello"}, 422), 
        ({"prompt": "", "user_id": "usr_123"}, 422), # invalid prompt length
        ({"prompt": "A" * 5001, "user_id": "usr_123"}, 422) # invalid prompt length
    ]
)
def test_process_secure_prompt_validation_failures(client, invalid_payload, expected_status):
    """
    GIVEN invalid payloads
    WHEN a POST request is made to /v1/privacy/chat
    THEN the gateway should automatically reject it with a 422 Unprocessable Entity status
    """
    response = client.post("/v1/privacy/chat", json=invalid_payload)
    assert response.status_code == expected_status


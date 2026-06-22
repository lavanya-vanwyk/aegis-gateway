from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone

class PromptRequest(BaseModel):
    prompt: str = Field(
        ..., 
        min_length=1, 
        max_length=5000, 
        description="The raw text prompt containing potential PII to be processed by the LLM."
    )
    user_id: str = Field(
        ..., 
        description="Unique identifier for the client user making the request, useful for tracking sessions or custom rules."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "Can you review this contract for Lavanya van Wyk, ID number 0101015009087? You can email her at lavanya@example.com.",
                "user_id": "usr_94823"
            }
        }
    }


class PromptResponse(BaseModel):
    status: str = Field("success", description="The status of the request execution.")
    processed_response: str = Field(..., description="The final, fully rehydrated text response returned from the LLM.")
    entities_masked_count: int = Field(..., description="The total number of sensitive PII entities intercepted and protected.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        description="The UTC timestamp of the completed transaction."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "processed_response": "The contract for Lavanya van Wyk under ID 0101015009087 is valid, and an email can be sent to lavanya@example.com.",
                "entities_masked_count": 3,
                "timestamp": "2026-06-22T11:40:00Z"
            }
        }
    }


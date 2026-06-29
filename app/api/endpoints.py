from fastapi import APIRouter, HTTPException
from app.api.schemas import PromptRequest, PromptResponse
from app.services.masking import PrivacyMaskingService
from datetime import datetime, timezone

router = APIRouter(prefix="/v1/privacy", tags=["Privacy Gateway"])

# Initialize the heavy NLP service once at startup
masking_service = PrivacyMaskingService()


@router.post("/chat", response_model=PromptResponse)
async def process_secure_prompt(payload: PromptRequest):
    try:

        masking_result = await masking_service.mask_text(payload.prompt)

        anonymized_prompt = masking_result["anonymized_text"]
        entities_count = masking_result["entities_masked_count"]

        mock_llm_reply = f"System received safe prompt: {anonymized_prompt}"

        return PromptResponse(
            status="success",
            processed_response=mock_llm_reply,
            entities_masked_count=entities_count,
            timestamp=datetime.now(timezone.utc),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal gateway error: {str(e)}")

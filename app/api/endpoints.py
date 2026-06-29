from fastapi import APIRouter, HTTPException, Depends
from fastapi import APIRouter, HTTPException
from app.api.schemas import PromptRequest, PromptResponse
from app.services.masking import PrivacyMaskingService
from app.core.security import get_api_key
from app.services.rate_limiter import check_rate_limit
from datetime import datetime, timezone

router = APIRouter(prefix="/v1/privacy", tags=["Privacy Gateway"])

# Initialize the heavy NLP service once at startup
masking_service = PrivacyMaskingService()


async def verify_and_rate_limit(api_key: str = Depends(get_api_key)):
    await check_rate_limit(api_key)
    return api_key


@router.post("/chat", response_model=PromptResponse)
async def process_secure_prompt(
    payload: PromptRequest, api_key: str = Depends(verify_and_rate_limit)
):
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

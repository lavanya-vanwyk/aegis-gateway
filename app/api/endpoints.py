import time
from fastapi import APIRouter, HTTPException, Depends
from fastapi import APIRouter, HTTPException

from app.api.schemas import PromptRequest, PromptResponse
from app.services.masking import PrivacyMaskingService
from app.core.security import get_api_key
from app.services.rate_limiter import check_rate_limit
from app.core.logger import audit_logger
from app.services.llm import llm_service

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
    start_time = time.time()

    try:
        masking_result = await masking_service.mask_text(payload.prompt)
        anonymized_prompt = masking_result["anonymized_text"]
        entities_count = masking_result["entities_masked_count"]

        llm_reply = await llm_service.generate_response(anonymized_prompt)

        final_response = await masking_service.rehydrate_text(llm_reply)
        process_time_ms = round((time.time() - start_time) * 1000)

        audit_logger.info(
            "prompt_processed",
            extra={
                "audit_data": {
                    "user_id": payload.user_id,
                    "entities_masked_count": entities_count,
                    "process_time_ms": process_time_ms,
                    "status": "success",
                    "route": "/v1/privacy/chat",
                }
            },
        )

        return PromptResponse(
            status="success",
            processed_response=final_response,
            entities_masked_count=entities_count,
            timestamp=datetime.now(timezone.utc),
        )

    except Exception as e:
        audit_logger.error(
            "prompt_failed",
            extra={
                "audit_data": {
                    "user_id": payload.user_id if payload else "unknown",
                    "status": "error",
                    "error_detail": str(e),
                }
            },
        )
        raise HTTPException(status_code=500, detail=f"Internal gateway error: {str(e)}")

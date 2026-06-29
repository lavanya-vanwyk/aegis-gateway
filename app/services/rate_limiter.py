from fastapi import HTTPException, status
from app.core.database import redis_manager

RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60


async def check_rate_limit(api_key: str):
    """
    Sets a limit of 10 requests per minute per API Key.
    Raises a 429 Too Many Requests if the limit is exceeded.
    """
    client = redis_manager.client
    if not client:
        raise RuntimeError("Redis client pool is not initialized.")

    redis_key = f"rate_limit:{api_key}"

    current_count = await client.incr(redis_key)

    if current_count == 1:
        await client.expire(redis_key, RATE_LIMIT_WINDOW_SECONDS)

    if current_count > RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before trying again.",
        )

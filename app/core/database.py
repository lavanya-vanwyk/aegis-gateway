import asyncio
import redis.asyncio as aioredis
from app.core.config import settings


class RedisConnectionManager:
    def __init__(self):
        self.client = None

    async def connect(self):
        self.client = await aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            decode_responses=True,
            encoding="utf-8",
        )

        await self.client.ping()

    async def disconnect(self):
        if self.client:
            await self.client.aclose()


redis_manager = RedisConnectionManager()

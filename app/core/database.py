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

        # async_pool = aioredis.ConnectionPool(
        #     host="localhost", port=6379, db=0, decode_responses=True, max_connections=20
        # )

        # async_client = aioredis.Redis(connection_pool=async_pool)

        # await async_client.set("metric:hits", "42")
        # value = await async_client.get("metric:hits")
        # print(value)

        # Close the pool completely during application shutdown
        await async_client.aclose()

    asyncio.run(main())

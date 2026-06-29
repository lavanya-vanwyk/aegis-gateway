from app.core.database import redis_manager


class TokenVaultService:
    def __init__(self):
        # 5 minutes
        self.ttl_seconds = 300

    async def store_mapping(self, token_id: str, original_text: str) -> None:
        """
        Stores the token to original text mapping in Redis
        with expiration timer.
        """
        client = redis_manager.client
        if not client:
            raise RuntimeError("Redis client pool is not initialized.")

        await client.set(name=token_id, value=original_text, ex=self.ttl_seconds)

    async def retrieve_mapping(self, token_id: str) -> str | None:
        """
        Retrieves the original text and immediately deletes it from the vault.
        """
        client = redis_manager.client
        if not client:
            raise RuntimeError("Redis client pool is not initialized.")

        original_text = await client.getdel(name=token_id)

        return original_text

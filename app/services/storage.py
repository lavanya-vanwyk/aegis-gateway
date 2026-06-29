from app.core.database import redis_manager
from app.core.config import settings
from cryptography.fernet import Fernet


class TokenVaultService:
    def __init__(self):
        # 5 minutes
        self.ttl_seconds = 300
        if not getattr(settings, "VAULT_ENCRYPTION_KEY", None):
            raise ValueError(
                "Critical Security Error: VAULT_ENCRYPTION_KEY is missing."
            )

        self.cipher = Fernet(settings.VAULT_ENCRYPTION_KEY)

    async def store_mapping(self, token_id: str, original_text: str) -> None:
        """
        Stores the token to original text mapping in Redis
        with expiration timer.
        """
        client = redis_manager.client
        if not client:
            raise RuntimeError("Redis client pool is not initialized.")

        encrypted_payload = self.cipher.encrypt(original_text.encode("utf-8"))

        await client.set(name=token_id, value=encrypted_payload, ex=self.ttl_seconds)

    async def retrieve_mapping(self, token_id: str) -> str | None:
        """
        Retrieves the original text and immediately deletes it from the vault.
        """
        client = redis_manager.client
        if not client:
            raise RuntimeError("Redis client pool is not initialized.")

        encrypted_payload = await client.getdel(name=token_id)

        if encrypted_payload:
            decrypted_text = self.cipher.decrypt(encrypted_payload).decode("utf-8")
            return decrypted_text

        return None

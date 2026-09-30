from openai import AsyncOpenAI
from app.core.config import settings
import os


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="http://ollama_server:11434/v1", api_key="ollama"
        )
        self.system_prompt = (
            "You are a helpful assistant responding to a user. "
            "The user's prompt contains privacy placeholders enclosed in square brackets. "
            "You MUST incorporate those exact bracketed placeholders precisely as they "
            "appear in the prompt when referring to the user. "
            "CRITICAL: Do NOT invent, mimic, or generate your own bracketed placeholders "
            "for your own name, email, or signature. Write normally for yourself."
        )
        self.model_name = os.getenv("LLM_MODEL", "llama3")

    async def generate_response(self, prompt: str) -> str:
        """
        Sends the masked prompt to the external LLM asynchronously and returns the text reply.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=500,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"External LLM generation failed: {str(e)}")


llm_service = LLMService()

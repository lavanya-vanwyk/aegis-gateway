from openai import AsyncOpenAI
from app.core.config import settings


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.LLM_API_KEY)
        self.system_prompt = (
            "You are a highly capable AI assistant securely processing data behind a privacy gateway. "
            "The user prompts you receive will contain anonymized tokens in the format <ENTITY_TYPE_abc123>. "
            "You MUST preserve these tokens exactly as they appear in your response. "
            "Do not modify, translate, or strip the brackets from the tokens under any circumstances."
        )

    async def generate_response(self, prompt: str) -> str:
        """
        Sends the masked prompt to the external LLM asynchronously and returns the text reply.
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"External LLM generation failed: {str(e)}")


llm_service = LLMService()

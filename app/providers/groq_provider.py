from app.core.config import settings
from app.providers.base import BaseLLMProvider
from app.providers.mock_provider import mock_rewrite
from app.schemas.llm import RewritePayload, RewriteResponse


class GroqProvider(BaseLLMProvider):
    name = "groq"

    async def rewrite(self, payload: RewritePayload) -> RewriteResponse:
        if not settings.groq_api_key:
            return mock_rewrite(self.name, payload)
        _ = settings.groq_base_url
        _ = settings.groq_model
        return mock_rewrite(self.name, payload)

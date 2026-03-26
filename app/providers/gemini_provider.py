from app.core.config import settings
from app.providers.base import BaseLLMProvider
from app.providers.mock_provider import mock_rewrite
from app.schemas.llm import RewritePayload, RewriteResponse


class GeminiProvider(BaseLLMProvider):
    name = "gemini"

    async def rewrite(self, payload: RewritePayload) -> RewriteResponse:
        if not settings.gemini_api_key:
            return mock_rewrite(self.name, payload)
        _ = settings.gemini_base_url
        _ = settings.gemini_model
        return mock_rewrite(self.name, payload)

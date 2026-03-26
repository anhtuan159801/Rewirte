from app.core.config import settings
from app.providers.base import BaseLLMProvider
from app.providers.mock_provider import mock_rewrite
from app.schemas.llm import RewritePayload, RewriteResponse


class OpenRouterProvider(BaseLLMProvider):
    name = "openrouter"

    async def rewrite(self, payload: RewritePayload) -> RewriteResponse:
        if not settings.openrouter_api_key:
            return mock_rewrite(self.name, payload)
        _ = settings.openrouter_base_url
        _ = settings.openrouter_model
        return mock_rewrite(self.name, payload)

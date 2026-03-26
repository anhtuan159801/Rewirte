from app.schemas.llm import RewritePayload, RewriteResponse


class ProviderError(Exception):
    pass


class TemporaryProviderError(ProviderError):
    pass


class InvalidProviderResponse(ProviderError):
    pass


class BaseLLMProvider:
    name: str

    async def rewrite(self, payload: RewritePayload) -> RewriteResponse:
        raise NotImplementedError

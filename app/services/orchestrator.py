import logging
from datetime import datetime, timezone

from app.core.config import settings
from app.models.job import ProviderAttempt, RewriteResult, UnitStatus
from app.providers.base import InvalidProviderResponse, ProviderError, TemporaryProviderError
from app.providers.gemini_provider import GeminiProvider
from app.providers.groq_provider import GroqProvider
from app.providers.openrouter_provider import OpenRouterProvider
from app.schemas.llm import RewritePayload
from app.services.validator import ValidationError, validator

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self) -> None:
        self.providers = [GroqProvider(), OpenRouterProvider(), GeminiProvider()]

    async def process_unit(self, unit, context: dict) -> RewriteResult | None:
        payload = RewritePayload(
            section_title=context.get("section_title"),
            previous_paragraph=context.get("previous_paragraph"),
            current_paragraph=unit.original_text,
            next_paragraph=context.get("next_paragraph"),
            risk_type=unit.risk_type.value,
            similarity_score=unit.similarity_score,
            report_excerpt=unit.report_excerpt,
            source_reference=context.get("source_reference"),
        )

        for provider in self.providers:
            for attempt_number in range(settings.max_provider_retries + 1):
                started_at = datetime.now(timezone.utc)
                try:
                    response = await provider.rewrite(payload)
                    score = validator.validate(unit.original_text, response)
                    ended_at = datetime.now(timezone.utc)
                    unit.attempts.append(
                        ProviderAttempt(
                            provider_name=provider.name,
                            status="SUCCESS",
                            error_message=None,
                            latency_ms=int((ended_at - started_at).total_seconds() * 1000),
                            started_at=started_at,
                            ended_at=ended_at,
                        )
                    )
                    unit.status = UnitStatus.REWRITTEN
                    unit.selected_provider = provider.name
                    unit.rewritten_text = response.rewritten_text
                    unit.summary_of_changes = response.summary_of_changes
                    unit.citation_needed = response.citation_needed
                    unit.confidence = response.confidence
                    unit.validator_score = score
                    return RewriteResult(
                        provider_name=provider.name,
                        rewritten_text=response.rewritten_text,
                        summary_of_changes=response.summary_of_changes,
                        citation_needed=response.citation_needed,
                        confidence=response.confidence,
                        validator_score=score,
                        accepted=True,
                    )
                except (TemporaryProviderError, ProviderError, InvalidProviderResponse, ValidationError) as exc:
                    ended_at = datetime.now(timezone.utc)
                    logger.warning("provider failed", extra={"provider": provider.name, "unit_id": unit.id, "error": str(exc)})
                    unit.attempts.append(
                        ProviderAttempt(
                            provider_name=provider.name,
                            status=type(exc).__name__.upper(),
                            error_message=str(exc),
                            latency_ms=int((ended_at - started_at).total_seconds() * 1000),
                            started_at=started_at,
                            ended_at=ended_at,
                        )
                    )
                    if attempt_number >= settings.max_provider_retries:
                        break

        unit.status = UnitStatus.MANUAL_REVIEW
        unit.failure_reason = "All providers failed or output did not pass validation."
        return None


orchestrator = Orchestrator()

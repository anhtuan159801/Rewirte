from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(StrEnum):
    UPLOADED = "UPLOADED"
    PARSING = "PARSING"
    ALIGNING = "ALIGNING"
    REWRITING = "REWRITING"
    VALIDATING = "VALIDATING"
    BUILDING = "BUILDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class UnitStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    REWRITTEN = "REWRITTEN"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class RiskType(StrEnum):
    VERBATIM = "VERBATIM"
    CLOSE_PARAPHRASE = "CLOSE_PARAPHRASE"
    MISSING_CITATION = "MISSING_CITATION"
    OTHER = "OTHER"


@dataclass
class ProviderAttempt:
    provider_name: str
    status: str
    error_message: str | None
    latency_ms: int
    started_at: datetime
    ended_at: datetime


@dataclass
class RewriteResult:
    provider_name: str
    rewritten_text: str
    summary_of_changes: str
    citation_needed: bool
    confidence: float
    validator_score: float
    accepted: bool


@dataclass
class RepairUnit:
    id: str
    job_id: str
    paragraph_ref: str
    original_text: str
    report_excerpt: str | None
    matched_source_text: str | None
    risk_type: RiskType
    similarity_score: float
    status: UnitStatus = UnitStatus.PENDING
    selected_provider: str | None = None
    rewritten_text: str | None = None
    summary_of_changes: str | None = None
    citation_needed: bool | None = None
    confidence: float | None = None
    validator_score: float | None = None
    attempts: list[ProviderAttempt] = field(default_factory=list)
    failure_reason: str | None = None


@dataclass
class Job:
    id: str
    source_docx_path: str
    report_pdf_path: str
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    status: JobStatus = JobStatus.UPLOADED
    output_docx_path: str | None = None
    change_report_path: str | None = None
    progress: int = 0
    units: list[RepairUnit] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)
    error_message: str | None = None

from datetime import datetime

from pydantic import BaseModel

from app.models.job import JobStatus, RiskType, UnitStatus


class CreateJobResponse(BaseModel):
    job_id: str
    status: JobStatus


class UnitResponse(BaseModel):
    id: str
    paragraph_ref: str
    risk_type: RiskType
    similarity_score: float
    original_text: str
    report_excerpt: str | None = None
    provider_used: str | None = None
    rewritten_text: str | None = None
    summary_of_changes: str | None = None
    citation_needed: bool | None = None
    confidence: float | None = None
    status: UnitStatus
    failure_reason: str | None = None


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int
    created_at: datetime
    updated_at: datetime
    output_docx_path: str | None = None
    change_report_path: str | None = None
    error_message: str | None = None
    timeline: list[str]
    total_units: int
    rewritten_units: int
    manual_review_units: int
    provider_fail_count: int

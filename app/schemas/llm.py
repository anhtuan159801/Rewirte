from pydantic import BaseModel, Field


class RewritePayload(BaseModel):
    section_title: str | None = None
    previous_paragraph: str | None = None
    current_paragraph: str
    next_paragraph: str | None = None
    risk_type: str
    similarity_score: float
    report_excerpt: str | None = None
    source_reference: str | None = None
    language: str = "vi"


class RewriteResponse(BaseModel):
    rewritten_text: str = Field(min_length=1)
    summary_of_changes: str = Field(min_length=1)
    citation_needed: bool
    confidence: float = Field(ge=0.0, le=1.0)

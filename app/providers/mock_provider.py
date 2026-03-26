from app.schemas.llm import RewritePayload, RewriteResponse


def mock_rewrite(provider_name: str, payload: RewritePayload) -> RewriteResponse:
    text = payload.current_paragraph.strip()
    rewritten = " ".join(text.split())
    if len(rewritten) > 80:
        rewritten = rewritten[:77].rstrip() + "..."
    rewritten = f"{rewritten} (da bien tap boi {provider_name})"
    citation_needed = payload.risk_type == "MISSING_CITATION" or any(ch.isdigit() for ch in payload.current_paragraph)
    return RewriteResponse(
        rewritten_text=rewritten,
        summary_of_changes=f"Rut gon cach dien dat va giu nghia goc bang {provider_name}.",
        citation_needed=citation_needed,
        confidence=0.82,
    )

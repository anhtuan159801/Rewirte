from uuid import uuid4

from app.models.job import RepairUnit, RiskType
from app.utils.text import similarity


class AlignmentService:
    def generate_units(self, job_id: str, paragraphs: list[dict], excerpts: list[dict]) -> list[RepairUnit]:
        units: list[RepairUnit] = []

        for excerpt in excerpts:
            best_match = None
            best_score = 0.0
            for paragraph in paragraphs:
                score = similarity(excerpt["text"], paragraph["text"])
                if score > best_score:
                    best_score = score
                    best_match = paragraph

            if best_match is None:
                continue

            units.append(
                RepairUnit(
                    id=str(uuid4()),
                    job_id=job_id,
                    paragraph_ref=best_match["paragraph_ref"],
                    original_text=best_match["text"],
                    report_excerpt=excerpt["text"],
                    matched_source_text=best_match["text"],
                    risk_type=RiskType(excerpt["risk_type"]),
                    similarity_score=round(max(best_score, excerpt["similarity_score"]), 3),
                )
            )

        deduped: dict[str, RepairUnit] = {}
        for unit in units:
            existing = deduped.get(unit.paragraph_ref)
            if existing is None or unit.similarity_score > existing.similarity_score:
                deduped[unit.paragraph_ref] = unit
        return list(deduped.values())


alignment_service = AlignmentService()

import json
from pathlib import Path

from docx import Document

from app.models.job import Job, UnitStatus


class DocumentBuilder:
    def build(self, job: Job) -> tuple[str, str]:
        document = Document(job.source_docx_path)
        paragraph_map = {f"p_{index:04d}": paragraph for index, paragraph in enumerate(document.paragraphs, start=1)}

        for unit in job.units:
            if unit.status != UnitStatus.REWRITTEN or not unit.rewritten_text:
                continue
            paragraph = paragraph_map.get(unit.paragraph_ref)
            if paragraph is not None:
                paragraph.text = unit.rewritten_text

        output_path = Path(job.source_docx_path).with_name("revised.docx")
        document.save(output_path)

        report = {
            "job_id": job.id,
            "summary": {
                "total_units": len(job.units),
                "rewritten_units": len([unit for unit in job.units if unit.status == UnitStatus.REWRITTEN]),
                "manual_review_units": len([unit for unit in job.units if unit.status == UnitStatus.MANUAL_REVIEW]),
            },
            "units": [
                {
                    "unit_id": unit.id,
                    "paragraph_ref": unit.paragraph_ref,
                    "provider_used": unit.selected_provider,
                    "original_text": unit.original_text,
                    "rewritten_text": unit.rewritten_text,
                    "citation_needed": unit.citation_needed,
                    "confidence": unit.confidence,
                    "status": unit.status.value.lower(),
                }
                for unit in job.units
            ],
        }
        report_path = Path(job.source_docx_path).with_name("change_report.json")
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(output_path), str(report_path)


document_builder = DocumentBuilder()

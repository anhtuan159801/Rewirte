from datetime import datetime, timezone
from uuid import uuid4

from app.models.job import Job, JobStatus, UnitStatus
from app.repositories.job_repo import job_repository
from app.services.alignment_service import alignment_service
from app.services.docx_parser import docx_parser
from app.services.document_builder import document_builder
from app.services.orchestrator import orchestrator
from app.services.pdf_parser import pdf_parser


class JobService:
    def create_job(self, source_docx_path: str, report_pdf_path: str) -> Job:
        job = Job(id=str(uuid4()), source_docx_path=source_docx_path, report_pdf_path=report_pdf_path)
        job.timeline.append("Job created and files stored.")
        return job_repository.add(job)

    async def process_job(self, job_id: str) -> None:
        job = job_repository.get(job_id)
        if job is None:
            return
        try:
            job.status = JobStatus.PARSING
            job.progress = 10
            job.timeline.append("Parsing DOCX and PDF inputs.")
            docx_data = docx_parser.parse(job.source_docx_path)
            pdf_data = pdf_parser.parse(job.report_pdf_path)

            job.status = JobStatus.ALIGNING
            job.progress = 30
            job.timeline.append("Aligning suspicious report excerpts with DOCX paragraphs.")
            job.units = alignment_service.generate_units(job.id, docx_data["paragraphs"], pdf_data["excerpts"])

            job.status = JobStatus.REWRITING
            job.progress = 50
            for unit in job.units:
                unit.status = UnitStatus.PROCESSING
                context = self._build_context(docx_data["paragraphs"], unit.paragraph_ref)
                result = await orchestrator.process_unit(unit, context)
                if result is None:
                    job.timeline.append(f"Unit {unit.paragraph_ref} moved to manual review.")
                else:
                    job.timeline.append(f"Unit {unit.paragraph_ref} rewritten by {result.provider_name}.")

            job.status = JobStatus.VALIDATING
            job.progress = 75
            job.timeline.append("Validation step completed as part of provider orchestration.")

            job.status = JobStatus.BUILDING
            job.progress = 90
            job.timeline.append("Building revised DOCX and change report.")
            output_docx_path, report_path = document_builder.build(job)
            job.output_docx_path = output_docx_path
            job.change_report_path = report_path

            manual_review_units = len([unit for unit in job.units if unit.status == UnitStatus.MANUAL_REVIEW])
            job.status = JobStatus.MANUAL_REVIEW if manual_review_units else JobStatus.COMPLETED
            job.progress = 100
            job.timeline.append("Job finished.")
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            job.timeline.append(f"Job failed: {exc}")
        finally:
            job.updated_at = datetime.now(timezone.utc)

    def _build_context(self, paragraphs: list[dict], paragraph_ref: str) -> dict:
        current_index = next((index for index, item in enumerate(paragraphs) if item["paragraph_ref"] == paragraph_ref), None)
        if current_index is None:
            return {}
        current = paragraphs[current_index]
        previous_paragraph = paragraphs[current_index - 1]["text"] if current_index > 0 else None
        next_paragraph = paragraphs[current_index + 1]["text"] if current_index < len(paragraphs) - 1 else None
        return {
            "section_title": current.get("section"),
            "previous_paragraph": previous_paragraph,
            "next_paragraph": next_paragraph,
            "source_reference": current.get("paragraph_ref"),
        }


job_service = JobService()

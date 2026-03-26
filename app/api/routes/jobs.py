from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.models.job import UnitStatus
from app.repositories.job_repo import job_repository
from app.schemas.job import CreateJobResponse, JobResponse, UnitResponse
from app.services.file_processor import file_processor
from app.services.job_service import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=CreateJobResponse)
async def create_job(
    background_tasks: BackgroundTasks,
    source_docx: UploadFile = File(...),
    report_pdf: UploadFile = File(...),
) -> CreateJobResponse:
    if not source_docx.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="source_docx must be a DOCX file")
    if not report_pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="report_pdf must be a PDF file")

    temp_job = job_service.create_job(source_docx_path="", report_pdf_path="")
    source_path = file_processor.save_upload(temp_job.id, source_docx, "source.docx")
    report_path = file_processor.save_upload(temp_job.id, report_pdf, "report.pdf")
    temp_job.source_docx_path = source_path
    temp_job.report_pdf_path = report_path

    background_tasks.add_task(job_service.process_job, temp_job.id)
    return CreateJobResponse(job_id=temp_job.id, status=temp_job.status)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    job = job_repository.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    provider_fail_count = sum(1 for unit in job.units for attempt in unit.attempts if attempt.status != "SUCCESS")
    rewritten_units = len([unit for unit in job.units if unit.status == UnitStatus.REWRITTEN])
    manual_review_units = len([unit for unit in job.units if unit.status == UnitStatus.MANUAL_REVIEW])
    return JobResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at,
        updated_at=job.updated_at,
        output_docx_path=job.output_docx_path,
        change_report_path=job.change_report_path,
        error_message=job.error_message,
        timeline=job.timeline,
        total_units=len(job.units),
        rewritten_units=rewritten_units,
        manual_review_units=manual_review_units,
        provider_fail_count=provider_fail_count,
    )


@router.get("/{job_id}/units", response_model=list[UnitResponse])
async def get_units(job_id: str) -> list[UnitResponse]:
    job = job_repository.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return [
        UnitResponse(
            id=unit.id,
            paragraph_ref=unit.paragraph_ref,
            risk_type=unit.risk_type,
            similarity_score=unit.similarity_score,
            original_text=unit.original_text,
            report_excerpt=unit.report_excerpt,
            provider_used=unit.selected_provider,
            rewritten_text=unit.rewritten_text,
            summary_of_changes=unit.summary_of_changes,
            citation_needed=unit.citation_needed,
            confidence=unit.confidence,
            status=unit.status,
            failure_reason=unit.failure_reason,
        )
        for unit in job.units
    ]


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(job_id: str, background_tasks: BackgroundTasks) -> JobResponse:
    job = job_repository.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    background_tasks.add_task(job_service.process_job, job.id)
    return await get_job(job_id)


@router.get("/{job_id}/download/docx")
async def download_docx(job_id: str) -> FileResponse:
    job = job_repository.get(job_id)
    if job is None or not job.output_docx_path:
        raise HTTPException(status_code=404, detail="Output DOCX not found")
    return FileResponse(job.output_docx_path, filename="revised.docx")


@router.get("/{job_id}/download/report")
async def download_report(job_id: str) -> FileResponse:
    job = job_repository.get(job_id)
    if job is None or not job.change_report_path:
        raise HTTPException(status_code=404, detail="Change report not found")
    return FileResponse(job.change_report_path, filename="change_report.json")

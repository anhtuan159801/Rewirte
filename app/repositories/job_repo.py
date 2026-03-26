from collections.abc import Iterable

from app.models.job import Job


class JobRepository:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def add(self, job: Job) -> Job:
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def list(self) -> Iterable[Job]:
        return self._jobs.values()


job_repository = JobRepository()

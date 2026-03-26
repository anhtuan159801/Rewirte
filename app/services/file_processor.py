from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class FileProcessor:
    def create_job_dir(self, job_id: str) -> Path:
        path = settings.storage_path / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_upload(self, job_id: str, file: UploadFile, target_name: str) -> str:
        job_dir = self.create_job_dir(job_id)
        target_path = job_dir / f"{uuid4()}_{target_name}"
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return str(target_path)


file_processor = FileProcessor()

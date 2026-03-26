from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(title="DOCX Rewrite System", version="0.1.0")
static_dir = Path(__file__).resolve().parent / "static"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def root_ui() -> FileResponse:
    return FileResponse(static_dir / "index.html")


app.include_router(health_router)
app.include_router(jobs_router)

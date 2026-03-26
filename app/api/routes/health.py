from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def root() -> dict[str, object]:
    return {
        "service": "docx-rewrite-system",
        "status": "ok",
        "docs_url": "/docs",
        "health_url": "/health",
        "routes": [
            "/",
            "/health",
            "/healthz",
            "/ready",
            "/docs",
            "/jobs",
        ],
    }


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}

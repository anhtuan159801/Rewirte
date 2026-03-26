from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@router.get("/system/info")
def system_info() -> dict[str, object]:
    return {
        "service": "docx-rewrite-system",
        "status": "ok",
        "ui_url": "/",
        "docs_url": "/docs",
        "health_url": "/health",
        "routes": [
            "/",
            "/health",
            "/healthz",
            "/ready",
            "/system/info",
            "/docs",
            "/jobs",
        ],
    }

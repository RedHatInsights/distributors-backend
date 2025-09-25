"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
@router.get("/livez")
@router.get("/readyz")
def health():
    """Get app health status."""
    return {"status": "success"}

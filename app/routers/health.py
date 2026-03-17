from fastapi import APIRouter
from app.services.logging import logger

router = APIRouter()


@router.get("/health")
def health_check():
    logger.info("Health check endpoint called.")
    return {"status": "ok", "service": "fakeradar-ai"}

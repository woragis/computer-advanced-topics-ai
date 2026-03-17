from fastapi import APIRouter
from app.services.logging import logger

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Returns service status and name.",
    response_description="Service is healthy.",
    responses={
        200: {
            "description": "Service is healthy.",
            "content": {
                "application/json": {
                    "example": {"status": "ok", "service": "fakeradar-ai"}
                }
            }
        }
    }
)
def health_check():
    logger.info("Health check endpoint called.")
    return {"status": "ok", "service": "fakeradar-ai"}

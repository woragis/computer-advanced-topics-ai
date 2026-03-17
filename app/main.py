
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import analysis, health
from app.services.logging import logger

app = FastAPI(
    title="FakeRadar AI Server",
    description="NLP pipeline for fake news detection",
    version="1.0.0"
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.include_router(health.router, prefix="/ai", tags=["Health"])
app.include_router(analysis.router, prefix="/ai", tags=["Analysis"])

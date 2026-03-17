
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import analysis, health
from app.services.logging import logger

app = FastAPI(
    title="FakeRadar AI Server",
    description="""
    FakeRadar AI Server provides NLP-powered fake news detection, claim extraction, fact-checking, and credibility scoring.
    
    ## Features
    - Analyze news articles or text for factual claims
    - Fact-check claims using external APIs
    - Score credibility and provide human-readable explanations
    
    ## Usage
    - Use `/ai/analyze` to analyze a URL or text
    - Use `/ai/health` to check service status
    
    ## Error Codes
    - 400: Bad request (missing input)
    - 422: Processing error (scraping, claim extraction, fact-checking, LLM)
    - 500: Internal server error
    """,
    version="1.0.0",
    contact={
        "name": "FakeRadar Team",
        "email": "support@fakeradar.ai"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.include_router(health.router, prefix="/ai", tags=["Health"])
app.include_router(analysis.router, prefix="/ai", tags=["Analysis"])

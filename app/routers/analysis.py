from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalysisRequest, AnalysisResult
from app.services.scraper import scrape_url
from app.services.claim_extractor import extract_claims
from app.services.fact_checker import fact_check_claims
from app.services.credibility_scorer import score_credibility
from app.services.logging import logger
from app.services.log_publisher import publish_log

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalysisResult,
    summary="Analyze Article or Text",
    description=(
        "Analyze a news article (by URL) or raw text for factual claims, fact-check them, and score credibility.\n\n"
        "- Provide either a URL or text (or both).\n"
        "- Returns extracted claims, fact-check results, credibility score, and explanation."
    ),
    response_description="Analysis result with claims, credibility score, and explanation.",
    responses={
        200: {
            "description": "Analysis completed successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "raw_text": "...article text...",
                        "credibility_score": 0.82,
                        "verdict": "RELIABLE",
                        "claims": [
                            {"text": "The Eiffel Tower is in Paris.", "is_verified": True,
                                "confidence": 0.9, "source_url": "https://factcheck.com/eiffel"}
                        ],
                        "sources": [
                            {"url": "https://example.com", "domain": "example.com",
                                "reputation_score": 0.95, "is_known_satire": False}
                        ],
                        "explanation": "The article is mostly factual and cites reputable sources."
                    }
                }
            }
        },
        400: {"description": "Missing input (url or text)."},
        422: {"description": "Processing error (scraping, claim extraction, fact-checking, LLM)."},
        500: {"description": "Internal server error."}
    }
)
async def analyze(request: AnalysisRequest):
    logger.info(
        f"Analyze endpoint called. url={request.url} text_len={len(request.text) if request.text else 0}")
    await publish_log(
        level="info",
        event="analysis.started",
        message="Analyze request received",
        metadata={
            "hasUrl": bool(request.url),
            "textLen": len(request.text) if request.text else 0,
        },
    )
    if not request.has_input():
        logger.warning("Analyze endpoint: missing input.")
        raise HTTPException(status_code=400, detail="Provide 'url' or 'text'")

    # Step 1 — Get raw text
    text = request.text
    if request.url and not text:
        try:
            text = await scrape_url(request.url)
        except Exception as e:
            logger.error(f"Error scraping URL {request.url}: {e}")
            raise HTTPException(
                status_code=422, detail="Failed to extract text from URL")

    # Step 2 — Extract factual claims
    try:
        claims_raw = extract_claims(text)
    except Exception as e:
        logger.error(f"Error extracting claims: {e}")
        raise HTTPException(
            status_code=422, detail="Failed to extract claims from text")

    # Step 3 — Fact-check each claim
    try:
        checked_claims = await fact_check_claims(claims_raw)
    except Exception as e:
        logger.error(f"Error fact-checking claims: {e}")
        raise HTTPException(
            status_code=422, detail="Failed to fact-check claims")

    # Step 4 — Score credibility (LLM)
    try:
        result = await score_credibility(text, checked_claims)
    except Exception as e:
        logger.error(f"Error scoring credibility: {e}")
        raise HTTPException(
            status_code=422, detail="Failed to score credibility")

    logger.info("Analyze endpoint completed successfully.")
    await publish_log(
        level="info",
        event="analysis.completed",
        message="Analyze request completed",
        metadata={
            "verdict": result.verdict.value,
            "credibilityScore": result.credibility_score,
            "claimsCount": len(result.claims),
        },
    )
    return result

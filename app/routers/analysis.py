from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalysisRequest, AnalysisResult
from app.services.scraper import scrape_url
from app.services.claim_extractor import extract_claims
from app.services.fact_checker import fact_check_claims
from app.services.credibility_scorer import score_credibility
from app.services.logging import logger

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze(request: AnalysisRequest):
    logger.info(
        f"Analyze endpoint called. url={request.url} text_len={len(request.text) if request.text else 0}")
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
    return result

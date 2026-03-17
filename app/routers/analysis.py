from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalysisRequest, AnalysisResult
from app.services.scraper import scrape_url
from app.services.claim_extractor import extract_claims
from app.services.fact_checker import fact_check_claims
from app.services.credibility_scorer import score_credibility

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze(request: AnalysisRequest):
    if not request.has_input():
        raise HTTPException(status_code=400, detail="Provide 'url' or 'text'")

    # Step 1 — Get raw text
    text = request.text
    if request.url and not text:
        text = await scrape_url(request.url)

    # Step 2 — Extract factual claims
    claims_raw = extract_claims(text)

    # Step 3 — Fact-check each claim
    checked_claims = await fact_check_claims(claims_raw)

    # Step 4 — Score credibility (LLM)
    result = await score_credibility(text, checked_claims)

    return result

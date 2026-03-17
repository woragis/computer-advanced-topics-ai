import httpx
from app.models.schemas import ClaimResult
from app.config import settings

FACT_CHECK_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


async def fact_check_claims(claims: list[str]) -> list[ClaimResult]:
    """
    For each claim, query Google Fact Check Tools API.
    Returns a list of ClaimResult with verification status.
    """
    results = []

    async with httpx.AsyncClient(timeout=10) as client:
        for claim_text in claims:
            try:
                response = await client.get(FACT_CHECK_URL, params={
                    "query": claim_text,
                    "key": settings.fact_check_api_key,
                    "languageCode": "en"
                })
                data = response.json()
                claims_found = data.get("claims", [])

                if claims_found:
                    rating = claims_found[0].get("claimReview", [{}])[0]
                    source_url = rating.get("url", "")
                    text_rating = rating.get("textualRating", "").lower()
                    is_verified = "true" in text_rating or "correct" in text_rating
                    results.append(ClaimResult(
                        text=claim_text,
                        is_verified=is_verified,
                        confidence=0.85,
                        source_url=source_url
                    ))
                else:
                    results.append(ClaimResult(
                        text=claim_text,
                        is_verified=False,
                        confidence=0.3,
                        source_url=None
                    ))

            except Exception:
                results.append(ClaimResult(
                    text=claim_text,
                    is_verified=False,
                    confidence=0.1,
                    source_url=None
                ))

    return results

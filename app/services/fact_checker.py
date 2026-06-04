import httpx
from app.models.schemas import ClaimResult, SourceResult
from app.config import settings

FACT_CHECK_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
SERPER_URL = "https://google.serper.dev/search"

TRUSTED_NEWS_HINTS = (
    "g1.globo",
    "reuters",
    "afp.com",
    "bbc.",
    "apnews",
    "folha",
    "estadao",
)


def _language_for_claim(text: str) -> str:
    pt_hints = (" da ", " de ", " que ", " não ", "ção", "ã", "õ", "á", "é")
    lower = text.lower()
    if any(h in lower for h in pt_hints):
        return "pt"
    return "en"


async def _serper_corroborate(client: httpx.AsyncClient, claim_text: str) -> ClaimResult | None:
    if not settings.serper_api_key:
        return None
    query = claim_text[:120]
    try:
        response = await client.post(
            SERPER_URL,
            headers={"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"},
            json={"q": query, "gl": "br", "hl": "pt-br", "num": 5},
            timeout=12,
        )
        response.raise_for_status()
        data = response.json()
        for hit in data.get("organic", []):
            link = (hit.get("link") or "").lower()
            if any(h in link for h in TRUSTED_NEWS_HINTS):
                return ClaimResult(
                    text=claim_text,
                    is_verified=True,
                    confidence=0.78,
                    source_url=hit.get("link"),
                )
    except Exception:
        return None
    return None


async def fact_check_claims(claims: list[str]) -> list[ClaimResult]:
    """
    Verify claims via Google Fact Check API when configured, then Serper fallback.
    If nothing is found, mark as UNKNOWN (not false) — confidence ~0.5.
    """
    results: list[ClaimResult] = []

    async with httpx.AsyncClient(timeout=12) as client:
        for claim_text in claims:
            verified_via_fc = False

            if settings.fact_check_api_key:
                try:
                    lang = _language_for_claim(claim_text)
                    response = await client.get(
                        FACT_CHECK_URL,
                        params={
                            "query": claim_text[:200],
                            "key": settings.fact_check_api_key,
                            "languageCode": lang,
                        },
                    )
                    data = response.json()
                    claims_found = data.get("claims", [])

                    if claims_found:
                        rating = claims_found[0].get("claimReview", [{}])[0]
                        source_url = rating.get("url", "")
                        text_rating = (rating.get("textualRating") or "").lower()
                        is_false = any(
                            w in text_rating
                            for w in ("false", "fake", "falso", "enganoso", "incorrect")
                        )
                        is_true = any(
                            w in text_rating
                            for w in ("true", "correct", "verdade", "correto", "verified")
                        )
                        if is_false:
                            results.append(
                                ClaimResult(
                                    text=claim_text,
                                    is_verified=False,
                                    confidence=0.15,
                                    source_url=source_url or None,
                                )
                            )
                            verified_via_fc = True
                        elif is_true:
                            results.append(
                                ClaimResult(
                                    text=claim_text,
                                    is_verified=True,
                                    confidence=0.88,
                                    source_url=source_url or None,
                                )
                            )
                            verified_via_fc = True
                except Exception:
                    pass

            if verified_via_fc:
                continue

            serper_hit = await _serper_corroborate(client, claim_text)
            if serper_hit:
                results.append(serper_hit)
                continue

            # Sem evidência de falsidade — inconclusivo, NÃO contar como fake
            results.append(
                ClaimResult(
                    text=claim_text,
                    is_verified=False,
                    confidence=0.5,
                    source_url=None,
                )
            )

    return results


def build_source_results(source_url: str | None) -> list[SourceResult]:
    from app.services.source_reputation import domain_from_url, get_domain_reputation

    if not source_url:
        return []
    domain = domain_from_url(source_url) or source_url
    return [
        SourceResult(
            url=source_url,
            domain=domain,
            reputation_score=get_domain_reputation(source_url),
            is_known_satire=False,
        )
    ]

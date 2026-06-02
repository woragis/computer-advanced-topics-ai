import anthropic
from app.models.schemas import ClaimResult, AnalysisResult, Verdict
from app.config import settings

client = anthropic.Anthropic(api_key=settings.llm_api_key) if settings.llm_api_key else None


def _mock_score(text: str, claims: list[ClaimResult]) -> AnalysisResult:
    verified_count = sum(1 for c in claims if c.is_verified)
    total_claims = len(claims) or 1
    score = round(verified_count / total_claims, 2)
    if score >= 0.7:
        verdict = Verdict.RELIABLE
    elif score >= 0.4:
        verdict = Verdict.SUSPICIOUS
    else:
        verdict = Verdict.FAKE
    return AnalysisResult(
        raw_text=text,
        credibility_score=score,
        verdict=verdict,
        claims=claims,
        sources=[],
        explanation=(
            "Mock analysis (AI_MOCK_LLM enabled): score based on claim verification ratio. "
            "Set LLM_API_KEY and AI_MOCK_LLM=false for real LLM scoring."
        ),
    )


async def score_credibility(text: str, claims: list[ClaimResult]) -> AnalysisResult:
    """
    Use LLM to assign a credibility score and verdict
    based on the article text and claim verification results.
    """
    if settings.ai_mock_llm or not settings.llm_api_key:
        return _mock_score(text, claims)

    claim_summary = "\n".join(
        f"- {'✅' if c.is_verified else '❌'} {c.text}" for c in claims
    )

    prompt = f"""You are a misinformation analyst. Given the article excerpt and claim verification results below, provide:
1. A credibility score between 0.0 (completely fake) and 1.0 (fully credible)
2. A verdict: RELIABLE, SUSPICIOUS, or FAKE
3. A 2-sentence explanation for a general audience

Article excerpt (first 1000 chars):
{text[:1000]}

Claim verification results:
{claim_summary}

Respond ONLY in this JSON format (no markdown):
{{
  \"credibility_score\": 0.0,
  \"verdict\": \"SUSPICIOUS\",
  \"explanation\": "..."
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    llm_output = json.loads(message.content[0].text)

    score = float(llm_output["credibility_score"])
    verdict_str = llm_output["verdict"]
    explanation = llm_output["explanation"]

    return AnalysisResult(
        raw_text=text,
        credibility_score=score,
        verdict=Verdict(verdict_str),
        claims=claims,
        sources=[],
        explanation=explanation
    )

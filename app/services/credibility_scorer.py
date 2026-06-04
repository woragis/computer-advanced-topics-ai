import json
import re
from datetime import datetime, timezone

import anthropic

from app.models.schemas import ClaimResult, AnalysisResult, Verdict
from app.config import settings
from app.services.source_reputation import get_domain_reputation

client = anthropic.Anthropic(api_key=settings.llm_api_key) if settings.llm_api_key else None


def _claim_status(c: ClaimResult) -> str:
    if c.is_verified:
        return "confirmed"
    if c.confidence <= 0.35:
        return "contradicted"
    return "unknown"


def _heuristic_score(
    claims: list[ClaimResult], source_url: str | None
) -> tuple[float, Verdict]:
    if not claims:
        rep = get_domain_reputation(source_url)
        score = min(0.75, rep)
        verdict = Verdict.RELIABLE if score >= 0.7 else Verdict.SUSPICIOUS
        return round(score, 2), verdict

    confirmed = sum(1 for c in claims if _claim_status(c) == "confirmed")
    contradicted = sum(1 for c in claims if _claim_status(c) == "contradicted")
    unknown = len(claims) - confirmed - contradicted

    rep = get_domain_reputation(source_url)
    ratio = confirmed / len(claims)
    score = ratio * 0.55 + (unknown / len(claims)) * 0.35 + rep * 0.25
    score -= (contradicted / len(claims)) * 0.5
    score = max(0.0, min(1.0, score))

    if contradicted >= 2 or (contradicted >= 1 and confirmed == 0):
        verdict = Verdict.FAKE
    elif score >= 0.65 and contradicted == 0:
        verdict = Verdict.RELIABLE
    elif score >= 0.4:
        verdict = Verdict.SUSPICIOUS
    else:
        verdict = Verdict.FAKE

    return round(score, 2), verdict


def _mock_score(
    text: str, claims: list[ClaimResult], source_url: str | None
) -> AnalysisResult:
    score, verdict = _heuristic_score(claims, source_url)
    from app.services.fact_checker import build_source_results

    return AnalysisResult(
        raw_text=text,
        credibility_score=score,
        verdict=verdict,
        claims=claims,
        sources=build_source_results(source_url),
        explanation=(
            "Análise heurística (sem LLM ou AI_MOCK_LLM): score combina veículo, "
            "alegações confirmadas e inconclusivas. Ausência de fact-check não significa falso."
        ),
    )


def _parse_llm_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def score_credibility(
    text: str,
    claims: list[ClaimResult],
    source_url: str | None = None,
) -> AnalysisResult:
    from app.services.fact_checker import build_source_results

    sources = build_source_results(source_url)
    rep = get_domain_reputation(source_url)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if settings.ai_mock_llm or not settings.llm_api_key:
        return _mock_score(text, claims, source_url)

    claim_summary = "\n".join(
        f"- [{_claim_status(c).upper()}] {c.text}" for c in claims
    )

    prompt = f"""You are a misinformation analyst. Today's reference date is {today} (UTC).
Score news REPORTING from established outlets — do not mark as fake solely because fact-check APIs returned no match.

Rules:
- "unknown" claims were NOT disproven; do not treat them as false.
- Photo caption dates are metadata, not proof the story is fabricated.
- If the source domain is a major news site (e.g. g1.globo.com) and nothing was contradicted, prefer RELIABLE or SUSPICIOUS over FAKE.
- Reserve FAKE for clear fabrication or contradicted core facts.
- Write the explanation in Portuguese (Brazil).

Source URL: {source_url or "text only"}
Source reputation (0-1): {rep:.2f}

Article excerpt (first 1500 chars):
{text[:1500]}

Claim verification:
{claim_summary or "(no individual claims extracted)"}

Respond ONLY with JSON (no markdown):
{{
  "credibility_score": 0.75,
  "verdict": "RELIABLE",
  "explanation": "..."
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    llm_output = _parse_llm_json(message.content[0].text)

    score = float(llm_output["credibility_score"])
    verdict_str = llm_output["verdict"]
    explanation = llm_output["explanation"]

    contradicted = sum(1 for c in claims if _claim_status(c) == "contradicted")
    if rep >= 0.85 and contradicted == 0 and score < 0.55:
        score = max(score, 0.62)

    score = max(0.0, min(1.0, score))

    return AnalysisResult(
        raw_text=text,
        credibility_score=round(score, 2),
        verdict=Verdict(verdict_str),
        claims=claims,
        sources=sources,
        explanation=explanation,
    )

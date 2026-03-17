from pydantic import BaseModel, field_validator, ValidationError, model_validator
from typing import Optional, List
from enum import Enum


class Verdict(str, Enum):
    RELIABLE = "RELIABLE"
    SUSPICIOUS = "SUSPICIOUS"
    FAKE = "FAKE"

# ── Request ──────────────────────────────────────────────────


class AnalysisRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None

    @model_validator(mode="after")
    def check_input(cls, values):
        if not (values.url or values.text):
            raise ValueError(
                "At least one of 'url' or 'text' must be provided.")
        return values

    def has_input(self) -> bool:
        return bool(self.url or self.text)

# ── Sub-models ───────────────────────────────────────────────


class ClaimResult(BaseModel):
    text: str
    is_verified: bool
    confidence: float           # 0.0 – 1.0
    source_url: Optional[str]

    @field_validator("confidence")
    def confidence_range(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")
        return v


class SourceResult(BaseModel):
    url: str
    domain: str
    reputation_score: float     # 0.0 – 1.0
    is_known_satire: bool

    @field_validator("reputation_score")
    def reputation_score_range(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("reputation_score must be between 0.0 and 1.0")
        return v

# ── Response ─────────────────────────────────────────────────


class AnalysisResult(BaseModel):
    raw_text: str
    credibility_score: float    # 0.0 – 1.0
    verdict: Verdict
    claims: List[ClaimResult]
    sources: List[SourceResult]
    explanation: str            # Human-readable LLM summary

    @field_validator("credibility_score")
    def credibility_score_range(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("credibility_score must be between 0.0 and 1.0")
        return v

# ── Basic Tests ─────────────────────────────────────────────


if __name__ == "__main__":
    # AnalysisRequest validation
    try:
        AnalysisRequest()
    except ValidationError as e:
        print("AnalysisRequest validation passed (missing input):", e)

    assert AnalysisRequest(url="http://test.com").has_input()
    assert AnalysisRequest(text="Some text").has_input()

    # ClaimResult confidence validation
    try:
        ClaimResult(text="test", is_verified=True,
                    confidence=1.2, source_url=None)
    except ValidationError as e:
        print("ClaimResult confidence validation passed:", e)

    # SourceResult reputation_score validation
    try:
        SourceResult(url="u", domain="d", reputation_score=-
                     0.1, is_known_satire=False)
    except ValidationError as e:
        print("SourceResult reputation_score validation passed:", e)

    # AnalysisResult credibility_score validation
    try:
        AnalysisResult(
            raw_text="t",
            credibility_score=1.5,
            verdict=Verdict.RELIABLE,
            claims=[],
            sources=[],
            explanation="e"
        )
    except ValidationError as e:
        print("AnalysisResult credibility_score validation passed:", e)

    print("All model validation tests passed.")

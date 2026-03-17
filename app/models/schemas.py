from pydantic import BaseModel
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

    def has_input(self) -> bool:
        return bool(self.url or self.text)

# ── Sub-models ───────────────────────────────────────────────


class ClaimResult(BaseModel):
    text: str
    is_verified: bool
    confidence: float           # 0.0 – 1.0
    source_url: Optional[str]


class SourceResult(BaseModel):
    url: str
    domain: str
    reputation_score: float     # 0.0 – 1.0
    is_known_satire: bool

# ── Response ─────────────────────────────────────────────────


class AnalysisResult(BaseModel):
    raw_text: str
    credibility_score: float    # 0.0 – 1.0
    verdict: Verdict
    claims: List[ClaimResult]
    sources: List[SourceResult]
    explanation: str            # Human-readable LLM summary

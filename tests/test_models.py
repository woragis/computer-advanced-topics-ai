import pytest
from app.models import schemas

# --- AnalysisRequest validation ---


def test_analysis_request_validation():
    with pytest.raises(Exception):
        schemas.AnalysisRequest()
    assert schemas.AnalysisRequest(url="http://test.com").has_input()
    assert schemas.AnalysisRequest(text="Some text").has_input()

# --- ClaimResult confidence validation ---


def test_claimresult_confidence():
    with pytest.raises(Exception):
        schemas.ClaimResult(text="test", is_verified=True,
                            confidence=1.2, source_url=None)
    schemas.ClaimResult(text="test", is_verified=True,
                        confidence=0.5, source_url=None)

# --- SourceResult reputation_score validation ---


def test_sourceresult_reputation_score():
    with pytest.raises(Exception):
        schemas.SourceResult(url="u", domain="d",
                             reputation_score=-0.1, is_known_satire=False)
    schemas.SourceResult(url="u", domain="d",
                         reputation_score=0.7, is_known_satire=False)

# --- AnalysisResult credibility_score validation ---


def test_analysisresult_credibility_score():
    with pytest.raises(Exception):
        schemas.AnalysisResult(
            raw_text="t",
            credibility_score=1.5,
            verdict=schemas.Verdict.RELIABLE,
            claims=[],
            sources=[],
            explanation="e"
        )
    schemas.AnalysisResult(
        raw_text="t",
        credibility_score=0.8,
        verdict=schemas.Verdict.RELIABLE,
        claims=[],
        sources=[],
        explanation="e"
    )

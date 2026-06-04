import re

import spacy

nlp = spacy.load("en_core_web_sm")

SKIP_RE = re.compile(
    r"^(foto:|—\s*foto:|agora no g1|resumo do dia|\*com informações)",
    re.IGNORECASE,
)
CAPTION_RE = re.compile(r"—\s*foto:", re.IGNORECASE)
MIN_WORDS = 8
MAX_CLAIMS = 8


def _is_noise(sentence: str) -> bool:
    s = sentence.strip()
    if len(s) < 40:
        return True
    if SKIP_RE.search(s):
        return True
    if CAPTION_RE.search(s) and s.count(".") < 2:
        return True
    if s.lower().startswith("o presidente") and "foto" in s.lower() and len(s) < 120:
        return True
    return False


def extract_claims(text: str) -> list[str]:
    """
    Extract verifiable factual sentences from article text.
    Filters captions, sidebar noise, and very short fragments.
    """
    doc = nlp(text[:12000])
    claims: list[str] = []

    for sent in doc.sents:
        raw = sent.text.strip()
        if _is_noise(raw):
            continue
        has_entity = any(
            ent.label_ in {"PERSON", "ORG", "GPE", "DATE", "EVENT"} for ent in sent.ents
        )
        if has_entity and len(raw.split()) >= MIN_WORDS:
            claims.append(raw)

    if len(claims) < 2:
        for part in re.split(r"(?<=[.!?])\s+", text[:8000]):
            part = part.strip()
            if _is_noise(part):
                continue
            if len(part.split()) >= MIN_WORDS and part not in claims:
                claims.append(part)

    seen: set[str] = set()
    unique: list[str] = []
    for c in claims:
        key = c.lower()[:80]
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique[:MAX_CLAIMS]

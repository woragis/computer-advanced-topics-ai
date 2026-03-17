import spacy

nlp = spacy.load("en_core_web_sm")


def extract_claims(text: str) -> list[str]:
    """
    Extract key factual claim sentences from article text.
    Uses spaCy to find sentences that contain named entities
    (people, organizations, dates, locations) — these are
    most likely to be verifiable factual claims.
    """
    doc = nlp(text)
    claims = []

    for sent in doc.sents:
        # Keep sentences with at least one named entity
        has_entity = any(
            ent.label_ in {"PERSON", "ORG", "GPE", "DATE", "EVENT"} for ent in sent.ents)
        if has_entity and len(sent.text.split()) > 6:
            claims.append(sent.text.strip())

    # Limit to top 10 most relevant claims
    return claims[:10]

from urllib.parse import urlparse

# Domínios de veículos estabelecidos (notícia institucional, não garantia de 100%)
KNOWN_DOMAINS: dict[str, float] = {
    "g1.globo.com": 0.92,
    "globo.com": 0.88,
    "bbc.com": 0.93,
    "reuters.com": 0.94,
    "apnews.com": 0.93,
    "afp.com": 0.92,
    "uol.com.br": 0.85,
    "folha.uol.com.br": 0.88,
    "estadao.com.br": 0.87,
}


def domain_from_url(url: str | None) -> str | None:
    if not url:
        return None
    try:
        host = urlparse(url).hostname or ""
        return host.lower().removeprefix("www.")
    except Exception:
        return None


def get_domain_reputation(url: str | None) -> float:
    domain = domain_from_url(url)
    if not domain:
        return 0.5
    if domain in KNOWN_DOMAINS:
        return KNOWN_DOMAINS[domain]
    for known, score in KNOWN_DOMAINS.items():
        if domain.endswith("." + known) or domain == known:
            return score
    return 0.55

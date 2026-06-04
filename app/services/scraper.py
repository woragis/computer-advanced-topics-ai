import httpx
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; FakeRadar/1.0; +https://fakeradar.local) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def _extract_paragraphs(root) -> str:
    paragraphs = root.find_all("p")
    return " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))


async def scrape_url(url: str) -> str:
    """Fetch a URL and extract clean article text."""
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=DEFAULT_HEADERS) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    text = ""

    # G1 / Globo article body
    article = soup.find("article") or soup.select_one(".mc-article-body") or soup.select_one(
        "[itemprop='articleBody']"
    )
    if article:
        text = _extract_paragraphs(article)

    if article:
        text = _extract_paragraphs(article)

    if len(text) < 100:
        text = _extract_paragraphs(soup.find("main") or soup.body or soup)

    # Remove blocos de sidebar comuns no G1
    for noise in ("Agora no g1", "Resumo do dia", "De segunda a sábado"):
        idx = text.find(noise)
        if idx > 200:
            text = text[:idx].strip()

    if len(text) < 100:
        raise ValueError("Could not extract meaningful text from URL")

    return text

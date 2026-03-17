import httpx
from bs4 import BeautifulSoup


async def scrape_url(url: str) -> str:
    """Fetch a URL and extract clean article text."""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Extract paragraphs
    paragraphs = soup.find_all("p")
    text = " ".join(p.get_text(strip=True) for p in paragraphs)

    if len(text) < 100:
        raise ValueError("Could not extract meaningful text from URL")

    return text

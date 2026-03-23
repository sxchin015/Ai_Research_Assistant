import logging
import requests
from config.config import SERPAPI_KEY, TAVILY_API_KEY

logger = logging.getLogger(__name__)

DDGS_AVAILABLE = False
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    pass

TAVILY_AVAILABLE = False
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    pass


def _tavily(query, max_results=5):
    """Search using Tavily and normalise results to title/href/body keys."""
    if not TAVILY_AVAILABLE:
        raise RuntimeError("tavily-python not installed.")
    client = TavilyClient(api_key=TAVILY_API_KEY)
    response = client.search(query=query, max_results=max_results)
    # Map Tavily keys (title, url, content) → existing format (title, href, body)
    return [
        {"title": r.get("title", ""), "href": r.get("url", ""), "body": r.get("content", "")}
        for r in response.get("results", [])
    ]


def _duckduckgo(query, max_results=5):
    if not DDGS_AVAILABLE:
        raise RuntimeError("duckduckgo-search not installed.")
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


def _serpapi(query, max_results=5):
    resp = requests.get(
        "https://serpapi.com/search",
        params={"q": query, "api_key": SERPAPI_KEY, "engine": "google", "num": max_results},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("organic_results", [])[:max_results]


def _format(results, source):
    if not results:
        return ""
    parts = [f"[Web results via {source}]\n"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        url = r.get("href") or r.get("link", "")
        snippet = r.get("body") or r.get("snippet", "")
        parts.append(f"{i}. {title}\n   {snippet}\n   {url}")
    return "\n\n".join(parts)


def web_search(query, max_results=5):
    # Priority: Tavily → SerpAPI → DuckDuckGo
    if TAVILY_API_KEY:
        try:
            results = _tavily(query, max_results)
            return _format(results, "Tavily"), "Tavily"
        except Exception as exc:
            logger.warning("Tavily failed: %s, falling back to SerpAPI/DuckDuckGo", exc)

    if SERPAPI_KEY:
        try:
            results = _serpapi(query, max_results)
            return _format(results, "SerpAPI"), "SerpAPI"
        except Exception as exc:
            logger.warning("SerpAPI failed: %s, falling back to DuckDuckGo", exc)

    results = _duckduckgo(query, max_results)
    return _format(results, "DuckDuckGo"), "DuckDuckGo"

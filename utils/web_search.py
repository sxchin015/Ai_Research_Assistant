import logging
import requests
from config.config import SERPAPI_KEY

logger = logging.getLogger(__name__)

DDGS_AVAILABLE = False
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    pass


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
    if SERPAPI_KEY:
        try:
            results = _serpapi(query, max_results)
            return _format(results, "SerpAPI"), "SerpAPI"
        except Exception as exc:
            logger.warning("SerpAPI failed: %s, falling back to DuckDuckGo", exc)

    results = _duckduckgo(query, max_results)
    return _format(results, "DuckDuckGo"), "DuckDuckGo"

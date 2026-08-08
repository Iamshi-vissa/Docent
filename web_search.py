"""
web_search.py - Internet search utility using DDGS (DuckDuckGo Search)
for retrieving web search results with title, URL, and snippet citations.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def perform_web_search(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    """
    Performs a web search using DDGS and returns structured search results.

    Args:
        query: User search query string.
        max_results: Maximum number of search results to retrieve (default: 4).

    Returns:
        List of dicts, each containing:
        - 'title': Page title
        - 'url': Web link URL
        - 'snippet': Short text excerpt from search result
    """
    if not query or not query.strip():
        return []

    results = []

    # Try importing ddgs or duckduckgo_search
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query.strip(), max_results=max_results))
            for item in raw_results:
                title = item.get("title") or "Web Result"
                url = item.get("href") or item.get("link") or ""
                snippet = item.get("body") or item.get("snippet") or ""
                if url:
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
    except Exception as e:
        logger.warning(f"Web search execution failed or timed out: {e}")

    return results

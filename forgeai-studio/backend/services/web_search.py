import urllib.request
import urllib.parse
import json
import re

_last_searched: bool = False

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ForgeAI/1.0)",
}

def _fetch(url: str, timeout: int = 4) -> str:
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")

def ddg_search(query: str) -> str | None:
    """DuckDuckGo Instant Answer API — free, no key required."""
    url = "https://api.duckduckgo.com/?q=" + urllib.parse.quote(query) + "&format=json&no_redirect=1&no_html=1&skip_disambig=1"
    try:
        data = json.loads(_fetch(url))
        abstract = data.get("AbstractText", "").strip()
        if abstract:
            source = data.get("AbstractSource", "")
            url_ref = data.get("AbstractURL", "")
            result = f"**{abstract}**"
            if source:
                result += f"\n\n*Source: {source}*"
                if url_ref:
                    result += f" — {url_ref}"
            return result
        # Try related topics
        topics = data.get("RelatedTopics", [])
        snippets = []
        for t in topics[:3]:
            text = t.get("Text", "") if isinstance(t, dict) else ""
            if text and len(text) > 20:
                snippets.append(f"- {text}")
        if snippets:
            return "Here's what I found:\n\n" + "\n".join(snippets)
    except Exception:
        pass
    return None

def google_search(query: str) -> str | None:
    """Scrape Google's featured snippet / first result description."""
    url = "https://www.google.com/search?q=" + urllib.parse.quote(query) + "&hl=en"
    try:
        html = _fetch(url, timeout=5)
        # Featured snippet
        m = re.search(r'<div[^>]*data-tts="answers"[^>]*>(.*?)</div>', html, re.DOTALL)
        if m:
            text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if text:
                return f"**{text}**\n\n*Source: Google*"
        # Knowledge panel description
        m = re.search(r'"description"\s*:\s*"([^"]{30,500})"', html)
        if m:
            return f"**{m.group(1)}**\n\n*Source: Google Knowledge Panel*"
    except Exception:
        pass
    return None

def web_lookup(query: str) -> str:
    """Try DuckDuckGo first, fall back to Google, then return a search link."""
    global _last_searched
    _last_searched = True
    result = ddg_search(query)
    if result:
        return f"### Web Search Result\n\n{result}"
    result = google_search(query)
    if result:
        return f"### Web Search Result\n\n{result}"
    encoded = urllib.parse.quote(query)
    return (
        f"I don't have that in my knowledge base. "
        f"[Search Google for \"{query}\"](https://www.google.com/search?q={encoded})"
    )

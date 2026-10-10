import requests
import feedparser
from urllib.parse import quote
from config import ARXIV_API, SEMANTIC_API


def search_arxiv(query: str, max_results: int = 5) -> list:
    """Search arXiv for papers. Returns list of dicts."""
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    r = requests.get(ARXIV_API, params=params, timeout=20)
    feed = feedparser.parse(r.content)

    papers = []
    for entry in feed.entries:
        papers.append({
            "title": entry.title.replace("\n", " ").strip(),
            "abstract": entry.summary.replace("\n", " ").strip(),
            "authors": [a.name for a in entry.authors],
            "url": entry.link,
            "pdf_url": next(
                (l.href for l in entry.links if l.type == "application/pdf"), ""
            ),
            "published": entry.published[:10],
            "source": "arxiv",
        })
    return papers


def search_semantic(query: str, limit: int = 5) -> list:
    """Search Semantic Scholar for papers. Adds citation counts."""
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,year,url,citationCount,venue",
    }
    try:
        r = requests.get(SEMANTIC_API, params=params, timeout=20)
        data = r.json().get("data", [])
        papers = []
        for p in data:
            papers.append({
                "title": p.get("title", ""),
                "abstract": (p.get("abstract") or "")[:2000],
                "authors": [a["name"] for a in (p.get("authors") or [])],
                "url": p.get("url", ""),
                "pdf_url": "",
                "published": str(p.get("year", "")),
                "citations": p.get("citationCount", 0),
                "venue": p.get("venue", ""),
                "source": "semantic_scholar",
            })
        return papers
    except Exception as e:
        print(f"[semantic] error: {e}")
        return []


def fetch_papers(query: str, n: int = 5) -> list:
    """Combined search — arXiv first, then Semantic Scholar."""
    arxiv = search_arxiv(query, n)
    semantic = search_semantic(query, n)

    # Merge and dedupe by title
    seen = set()
    merged = []
    for p in arxiv + semantic:
        key = p["title"].lower()[:60]
        if key not in seen:
            seen.add(key)
            merged.append(p)
    return merged[:n]


if __name__ == "__main__":
    papers = fetch_papers("Roman Urdu fake news", 5)
    for p in papers:
        print(f"[{p['source']}] {p['title']}")
        print(f"   {p.get('url', '')}")
        print()

import requests
import feedparser
from config import ARXIV_API, SEMANTIC_API


def _build_arxiv_query(query: str) -> str:
    """
    Build a proper AND query for arXiv.
    'low-resource NLP' -> 'all:"low-resource" AND all:"NLP"'
    Quoted phrases stay together.
    """
    parts = query.strip().split()
    clauses = []
    for part in parts:
        # If the user typed a quoted phrase, keep it
        if part.startswith('"') and part.endswith('"'):
            clauses.append(f"all:{part}")
        else:
            clauses.append(f'all:"{part}"')
    return " AND ".join(clauses)


def search_arxiv(query: str, max_results: int = 5) -> list:
    params = {
        "search_query": _build_arxiv_query(query),
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",       # <-- relevance, not date
        "sortOrder": "descending",
    }
    try:
        r = requests.get(ARXIV_API, params=params, timeout=20)
        feed = feedparser.parse(r.content)
    except Exception as e:
        print(f"[arxiv] error: {e}")
        return []

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


def _keyword_overlap(paper: dict, query: str) -> int:
    """Score a paper by how many query words appear in its title/abstract."""
    text = (paper.get("title", "") + " " + paper.get("abstract", "")).lower()
    words = [w.lower().strip('"') for w in query.split() if len(w) > 2]
    return sum(1 for w in words if w in text)


def fetch_papers(query: str, n: int = 5) -> list:
    """
    Combined search. Merges arXiv + Semantic Scholar, dedupes,
    and re-ranks by keyword overlap so the top results actually
    match the topic.
    """
    arxiv = search_arxiv(query, n * 2)
    semantic = search_semantic(query, n * 2)

    seen = set()
    merged = []
    for p in arxiv + semantic:
        key = p["title"].lower()[:60]
        if key and key not in seen:
            seen.add(key)
            merged.append(p)

    # Re-rank by keyword overlap
    merged.sort(key=lambda p: _keyword_overlap(p, query), reverse=True)

    # Drop papers with zero keyword overlap if we have better options
    scored = [(p, _keyword_overlap(p, query)) for p in merged]
    top_score = max((s for _, s in scored), default=0)
    if top_score > 0:
        merged = [p for p, s in scored if s > 0]

    return merged[:n]


if __name__ == "__main__":
    for p in fetch_papers("low-resource NLP", 3):
        print(p["title"], "|", p["url"])

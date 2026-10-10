import json
import os

from fetch import fetch_papers
from summarize import summarize_paper
from postgen import (
    generate_linkedin,
    generate_twitter_thread,
    generate_medium,
    generate_bluesky,
)

SEEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seen_papers.json")


def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(list(seen)), f, indent=2)


def _make_result(paper):
    summary = summarize_paper(paper)
    return {
        "paper": paper,
        "summary": summary,
        "linkedin": generate_linkedin(paper, summary),
        "twitter": generate_twitter_thread(paper, summary),
        "medium": generate_medium(paper, summary),
        "bluesky": generate_bluesky(paper, summary),
    }


def run(topic: str, n_papers: int = 3) -> list:
    """Original behavior. Returns the top N papers, even if seen before."""
    papers = fetch_papers(topic, n_papers)
    if not papers:
        return []
    return [_make_result(p) for p in papers]


def run_unique(topic: str, n_papers: int = 1, fetch_extra: int = 5) -> list:
    """
    Return N papers you haven't seen before. Tracks URLs in seen_papers.json.
    If no fresh papers are found, returns an empty list.
    """
    seen = load_seen()
    papers = fetch_papers(topic, fetch_extra)

    fresh = [p for p in papers if p.get("url", "") not in seen][:n_papers]

    if not fresh:
        print(f"No new papers on '{topic}'. All {len(papers)} results already seen.")
        return []

    results = []
    for p in fresh:
        results.append(_make_result(p))
        seen.add(p.get("url", ""))

    save_seen(seen)
    print(f"✅ Processed {len(results)} new paper(s). Total seen: {len(seen)}")
    return results


def reset_seen():
    """Delete the seen list. Start fresh."""
    if os.path.exists(SEEN_FILE):
        os.remove(SEEN_FILE)
        print("✅ seen_papers.json deleted")
    else:
        print("No seen list to delete")


def stats():
    """Show how many papers you've processed."""
    seen = load_seen()
    print(f"Papers seen: {len(seen)}")
    if seen:
        for url in sorted(seen):
            print(f"  {url}")

from fetch import fetch_papers
from summarize import summarize_paper
from postgen import (
    generate_linkedin,
    generate_twitter_thread,
    generate_medium,
    generate_bluesky,
)


def run(topic: str, n_papers: int = 3) -> list:
    """
    Full pipeline: search → summarize → generate posts.
    Returns a list of results, one per paper.
    """
    papers = fetch_papers(topic, n_papers)
    if not papers:
        return []

    results = []
    for paper in papers:
        summary = summarize_paper(paper)
        result = {
            "paper": paper,
            "summary": summary,
            "linkedin": generate_linkedin(paper, summary),
            "twitter": generate_twitter_thread(paper, summary),
            "medium": generate_medium(paper, summary),
            "bluesky": generate_bluesky(paper, summary),
        }
        results.append(result)

    return results

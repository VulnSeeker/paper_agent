import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

SUMMARY_PROMPT = """You are an NLP research assistant. Given a paper's title, authors, and abstract, extract a structured summary.

Return strict JSON with exactly these fields:

{
  "one_line": "one sentence, plain English, what this paper is about",
  "problem": "what problem does it solve? 2-3 sentences",
  "method": "how does it solve it? Be specific about models/datasets/techniques. 2-3 sentences",
  "result": "what are the key numbers/findings? 1-2 sentences",
  "why_it_matters": "why should anyone outside this subfield care? 1-2 sentences",
  "limitations": "what are the obvious limitations? 1-2 sentences",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}

Rules:
- Only use information from the provided title and abstract
- If a field is not visible in the abstract, write "Not stated in abstract"
- Do not invent results or numbers
- Keep it tight and factual
"""


def summarize_paper(paper: dict) -> dict:
    user_msg = f"""Title: {paper['title']}
Authors: {', '.join(paper.get('authors', [])[:5])}
Abstract: {paper['abstract']}

Return the JSON summary."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=4000,
        reasoning_effort="low",
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

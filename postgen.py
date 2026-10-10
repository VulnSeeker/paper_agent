import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)


def generate_linkedin(paper: dict, summary: dict) -> str:
    prompt = f"""Write a LinkedIn post about this paper.

Paper: {paper['title']}
Authors: {', '.join(paper.get('authors', [])[:3])}
Link: {paper.get('url', '')}

Summary:
- One line: {summary['one_line']}
- Problem: {summary['problem']}
- Method: {summary['method']}
- Result: {summary['result']}
- Why it matters: {summary['why_it_matters']}

Style rules:
- Start with a hook sentence that makes people stop scrolling
- 4-6 short paragraphs
- Use line breaks between paragraphs
- Conversational but professional
- Include one personal angle like "I read this paper this morning and..."
- End with a question or invitation to discuss
- Add 3-5 relevant hashtags at the end
- Do NOT use emojis
- Total length: 150-250 words

Return ONLY the post text."""

    return _call(prompt)


def generate_twitter_thread(paper: dict, summary: dict) -> list:
    prompt = f"""Write a Twitter/X thread about this paper.

Paper: {paper['title']}
Link: {paper.get('url', '')}

Summary:
- One line: {summary['one_line']}
- Problem: {summary['problem']}
- Method: {summary['method']}
- Result: {summary['result']}
- Why it matters: {summary['why_it_matters']}

Return strict JSON:
{{
  "tweets": [
    "tweet 1 (hook, under 280 chars)",
    "tweet 2 (problem, under 280 chars)",
    "tweet 3 (method, under 280 chars)",
    "tweet 4 (result, under 280 chars)",
    "tweet 5 (why it matters, under 280 chars)",
    "tweet 6 (link + closing)"
  ]
}}

Style rules:
- Each tweet under 280 characters
- First tweet a strong hook
- No emojis except max one in the whole thread
- Plain language

Return ONLY the JSON."""

    raw = _call(prompt)
    try:
        return json.loads(raw).get("tweets", [])
    except Exception:
        return [raw]


def generate_medium(paper: dict, summary: dict) -> str:
    prompt = f"""Write a Medium article about this paper.

Paper: {paper['title']}
Authors: {', '.join(paper.get('authors', [])[:3])}
Link: {paper.get('url', '')}

Summary:
- One line: {summary['one_line']}
- Problem: {summary['problem']}
- Method: {summary['method']}
- Result: {summary['result']}
- Why it matters: {summary['why_it_matters']}
- Limitations: {summary['limitations']}

Style rules:
- Start with a title (## heading)
- Then a subtitle in italic
- Opening paragraph: a story, question, or provocative claim
- Explain problem, method, result in plain English
- Include a "What this means" section
- End with a takeaway + paper link
- Total length: 400-600 words
- No emojis

Return ONLY the article text."""

    return _call(prompt)


def generate_bluesky(paper: dict, summary: dict) -> list:
    prompt = f"""Write 2-3 Bluesky posts about this paper.

Paper: {paper['title']}
Link: {paper.get('url', '')}

Summary:
- One line: {summary['one_line']}
- Result: {summary['result']}
- Why it matters: {summary['why_it_matters']}

Return strict JSON:
{{
  "posts": [
    "post 1 (under 300 chars)",
    "post 2 (under 300 chars)",
    "post 3 (under 300 chars, link + closing)"
  ]
}}

Style: casual, conversational, slightly nerdy. One emoji max.

Return ONLY the JSON."""

    raw = _call(prompt)
    try:
        return json.loads(raw).get("posts", [])
    except Exception:
        return [raw]


def _call(prompt: str) -> str:
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1200,
    )
    return response.choices[0].message.content.strip()

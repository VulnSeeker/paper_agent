import re
import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

def _clean(text: str) -> str:
    """Strip AI-tell characters and normalise punctuation."""
    if not text:
        return text
    # Replace U+2011 non-breaking hyphen with ASCII hyphen
    text = text.replace("\u2011", "-")
    # Replace em dash with comma + space
    text = text.replace("\u2014", ", ")
    # Replace en dash with hyphen
    text = text.replace("\u2013", "-")
    # Fix space before percent
    text = re.sub(r"(\d)\s+%", r"\1%", text)
    # Collapse multiple spaces
    text = re.sub(r"  +", " ", text)
    return text.strip()



STYLE_RULES = """
MANDATORY FORMAT. The output MUST include ALL of these, in order:
1. Hook line
2. What the paper is about (2-3 sentences)
3. What they found (1-2 sentences)
4. Why you read it and what you took away (use "I")
5. Paper URL on its own line
6. One real question
7. 3 to 5 hashtags

If any of steps 5, 6, or 7 are missing, the output is invalid. Always include them.

STRICT STYLE RULES. Violating any of these = failure.

1. NEVER use the em dash character. Not once. Not anywhere.
2. NEVER use the en dash character. Not once. Not anywhere.
3. NEVER use the non-breaking hyphen character (U+2011). Use a normal ASCII hyphen (-).
4. When you want a dash, use a comma, a period, or the word "and".
   Bad: "this plot, the one everyone uses, is wrong" (WRONG if you insert real dashes)
   Good: "this plot, the one everyone uses, is wrong"
   Bad: "tasks taking 2 to 30 minutes" (with dash between 2 and 30)
   Good: "tasks taking 2 to 30 minutes"
5. NEVER put a space before a percent sign. Write "5.5%" not "5.5 %".
6. NEVER say "we" about the paper's authors. You are not the author. You are a reader sharing what you found.
7. NEVER write like a summary or an abstract. Write like you are telling a smart friend about a paper you just read.
8. Use "I" when talking about your own reaction or what you took away.
9. Use "the authors" or "they" when referring to the paper's authors.
10. No emojis.
11. Banned words: delve, leverage, realm, landscape, navigate, underscore, showcase, intricate, pivotal, moreover, furthermore.
12. No AI filler. No "it is worth noting", no "in today's world", no "as we can see".
13. Split long sentences. If a sentence has more than one "and", break it into two.
"""


def generate_linkedin(paper, summary):
    prompt = f"""You are writing a LinkedIn post AS THE READER. The person posting this is not the author. They read the paper and are sharing their take.

Paper: {paper["title"]}
Link: {paper.get("url", "")}

What the paper is about:
- One line: {summary["one_line"]}
- Problem: {summary["problem"]}
- Method: {summary["method"]}
- Result: {summary["result"]}
- Why it matters: {summary["why_it_matters"]}

{STYLE_RULES}

Structure:
1. First line: a short hook. A reaction, a surprise, or a question you had while reading. Not a summary.
2. Second paragraph: what the paper is about, in your own words. Two or three sentences. Say "the authors" or "this paper".
3. Third paragraph: what they found. One or two sentences. The key result.
4. Fourth paragraph: why you cared enough to read it and what you took away. Use "I".
5. Fifth line: the paper link, plain, on its own line.
6. Sixth: one real question you actually want to know.
7. Hashtags: 3 to 5, at the very end.

Length: 150 to 250 words. Short sentences. Plain words.

Return ONLY the post text. No preamble, no explanation."""
    return _call(prompt)


def generate_twitter_thread(paper, summary):
    prompt = f"""You are writing a Twitter/X thread AS THE READER sharing a paper they just read.

Paper: {paper["title"]}
Link: {paper.get("url", "")}

Paper details:
- One line: {summary["one_line"]}
- Problem: {summary["problem"]}
- Method: {summary["method"]}
- Result: {summary["result"]}
- Why it matters: {summary["why_it_matters"]}

{STYLE_RULES}

Rules:
- Tweet 1: a hook. A reaction, a surprise, or a question. Not a summary.
- Tweets 2 to 5: explain the paper's problem, method, result, and importance. Say "the authors" or "they". Use "I" when sharing your reaction.
- Tweet 6: link to the paper and a closing line.
- Each tweet under 280 characters.
- Plain English. No jargon. No em dashes. No en dashes. No non-breaking hyphens.

Return strict JSON:
{{"tweets": ["tweet1", "tweet2", "tweet3", "tweet4", "tweet5", "tweet6"]}}"""
    raw = _call(prompt)
    try:
        return json.loads(raw).get("tweets", [])
    except Exception:
        return [raw]


def generate_medium(paper, summary):
    prompt = f"""You are writing a Medium article AS THE READER.

Paper: {paper["title"]}
Link: {paper.get("url", "")}

Paper details:
- One line: {summary["one_line"]}
- Problem: {summary["problem"]}
- Method: {summary["method"]}
- Result: {summary["result"]}
- Why it matters: {summary["why_it_matters"]}
- Limitations: {summary["limitations"]}

{STYLE_RULES}

Structure:
1. Title (## heading). Short, specific, interesting.
2. Subtitle in italic. One line.
3. Opening paragraph: a story from your own reading experience. Use "I".
4. What the paper is about. Say "the authors".
5. What they found. In plain words.
6. What this means. Why it matters beyond the paper.
7. What I took away. Use "I".
8. Paper link and a closing line.

Length: 500 to 800 words.

Return ONLY the article text."""
    return _call(prompt)


def generate_bluesky(paper, summary):
    prompt = f"""You are writing 2 or 3 Bluesky posts AS THE READER sharing a paper.

Paper: {paper["title"]}
Link: {paper.get("url", "")}

Paper details:
- One line: {summary["one_line"]}
- Result: {summary["result"]}
- Why it matters: {summary["why_it_matters"]}

{STYLE_RULES}
Bluesky tone: casual, honest, nerdy. One emoji maximum across all posts.

Rules:
- Post 1: your reaction. What surprised you. Use "I".
- Post 2: the key finding in plain words. Refer to authors as "they".
- Post 3: link and closing thought.

Each post under 300 characters. No em dashes. No en dashes. No non-breaking hyphens.

Return strict JSON:
{{"posts": ["post1", "post2", "post3"]}}"""
    raw = _call(prompt)
    try:
        return json.loads(raw).get("posts", [])
    except Exception:
        return [raw]


def _call(prompt):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.75,
        max_tokens=2500,
    )
    return _clean(response.choices[0].message.content)

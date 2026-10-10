markdown

# PaperPilot

Turn any research paper into a LinkedIn post, a Twitter thread, a Medium article, and a Bluesky drop — in one click.

## What it does

1. Searches arXiv and Semantic Scholar for papers on a topic
2. Reads the abstract with a Groq-hosted LLM
3. Extracts a structured summary (problem, method, result, why it matters)
4. Generates platform-specific posts: LinkedIn, Twitter/X thread, Medium article, Bluesky

## Stack

- Python 3.11
- Groq API (Llama 3.3 70B)
- arXiv API, Semantic Scholar API
- Streamlit UI

## Run it

```bash
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
streamlit run app.py

Status

Early prototype. Working on: better filtering, citation graphs, paper recommendations.
Author

Mubbshra Iqbal — GitHub

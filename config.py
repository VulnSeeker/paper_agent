import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "openai/gpt-oss-120b"

ARXIV_API = "http://export.arxiv.org/api/query"
SEMANTIC_API = "https://api.semanticscholar.org/graph/v1/paper/search"

MAX_SEARCH_RESULTS = 5
MAX_EVIDENCE_CHARS = 3000

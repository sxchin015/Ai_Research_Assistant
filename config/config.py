import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "4"))
MIN_RELEVANCE_SCORE = float(os.getenv("MIN_RELEVANCE_SCORE", "0.30"))

MODE_CONCISE = "Concise"
MODE_DETAILED = "Detailed"

SYSTEM_PROMPT_CONCISE = (
    "You are a precise research assistant. "
    "Answer in 2-3 sentences maximum. Be direct and factual. "
    "If context is provided, use it."
)

SYSTEM_PROMPT_DETAILED = (
    "You are an expert research assistant. "
    "Provide a thorough, well-structured answer using headings and bullet points. "
    "If context is provided from documents or web search, integrate it naturally."
)

def validate_config():
    warnings = []
    if not GROQ_API_KEY:
        warnings.append("GROQ_API_KEY not set. Get your free key at: https://console.groq.com")
    return warnings

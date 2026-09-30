import os

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock").lower()
LLM_CONCURRENCY: int = int(os.getenv("LLM_CONCURRENCY", "5"))
MOCK_LATENCY_MS: int = int(os.getenv("MOCK_LATENCY_MS", "200"))
MOCK_FAILURE_RATE: float = float(os.getenv("MOCK_FAILURE_RATE", "0.1"))

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")

VALID_CATEGORIES = [
    "Groceries",
    "Beverages",
    "Personal Care",
    "Household",
    "Electronics",
    "Fashion",
    "Home & Kitchen",
    "Other",
]

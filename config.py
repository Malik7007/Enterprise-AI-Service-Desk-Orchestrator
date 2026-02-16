import os
from dotenv import load_dotenv

load_dotenv()

# LLM Providers Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/v1")

# Default Model Selection
ACTIVE_PROVIDER = os.getenv("ACTIVE_PROVIDER", "openai")

# RAG Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
VECTOR_STORE_DIR = os.path.join(os.path.dirname(__file__), "vector_stores")

# Model Specialization Mapping
# Small/Fast models for simple logic, Large models for planning
MODEL_ROUTING = {
    "supervisor": "gpt-4o-mini" if ACTIVE_PROVIDER == "openai" else "llama3-8b-8192",
    "planner": "gpt-4o" if ACTIVE_PROVIDER == "openai" else "llama3-70b-8192",
    "domain_agent": "gpt-4o" if ACTIVE_PROVIDER == "openai" else "llama3-70b-8192",
    "privacy": "gpt-4o-mini" if ACTIVE_PROVIDER == "openai" else "llama3-8b-8192"
}

# Governance
PII_FILTER_ENABLED = True
LOG_PII_REDACTED = True

# LangSmith / Observability
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_PROJECT = "Enterprise_Service_Desk"

# Confidence Threshold
CONFIDENCE_THRESHOLD = 0.7

# Debug Mode
DEBUG_MODE = True

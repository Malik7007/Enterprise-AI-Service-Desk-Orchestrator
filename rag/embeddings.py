from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import DeterministicFakeEmbedding
from config import OPENAI_API_KEY
import os

def get_embeddings():
    """
    Returns the embeddings model. Uses OpenAI if key is present, 
    otherwise falls back to a deterministic fake to allow the system to start.
    """
    if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
        try:
            return OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        except Exception:
            pass
            
    # Fallback to local fake embeddings for zero-key startup stability
    return DeterministicFakeEmbedding(size=1536)

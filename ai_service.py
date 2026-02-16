from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, LOCAL_LLM_URL, ACTIVE_PROVIDER, MODEL_ROUTING

def get_llm(node_type="domain_agent", config=None):
    """
    Returns the configured LLM. Supports runtime configuration overrides.
    """
    # Use defaults from config if not provided in request
    provider = (config or {}).get("provider") or ACTIVE_PROVIDER
    model = (config or {}).get("model") or MODEL_ROUTING.get(node_type, "gpt-4o-mini")
    api_key = (config or {}).get("api_key")

    # Mapping provider to internal keys
    if not api_key:
        if provider == "openai": api_key = OPENAI_API_KEY
        elif provider == "groq": api_key = GROQ_API_KEY
        elif provider == "openrouter": api_key = OPENROUTER_API_KEY
        elif provider == "local": api_key = "none"

    # Handle missing keys gracefully for startup
    if not api_key and provider != "local":
        # Return a shell or default to avoid crash; real validation happens on use
        api_key = "sk-placeholder"

    if provider == "openai":
        return ChatOpenAI(api_key=api_key, model=model, temperature=0)
    
    elif provider == "groq":
        return ChatOpenAI(
            api_key=api_key,
            model=model,
            base_url="https://api.groq.com/openai/v1",
            temperature=0
        )
    
    elif provider == "openrouter":
        return ChatOpenAI(
            api_key=api_key,
            model=model,
            base_url="https://openrouter.ai/api/v1",
            temperature=0
        )
    
    elif provider == "local":
        return ChatOpenAI(
            api_key="none",
            model=model,
            base_url=LOCAL_LLM_URL,
            temperature=0
        )
    
    return ChatOpenAI(api_key=OPENAI_API_KEY or "sk-placeholder", model="gpt-4o", temperature=0)

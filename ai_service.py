from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from pydantic import Field
from typing import List, Optional, Any
import json
from config import OPENAI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, LOCAL_LLM_URL, ACTIVE_PROVIDER, MODEL_ROUTING

class MockLLM(BaseChatModel):
    """
    A deterministic mock LLM for testing when no real API keys are available.
    """
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        last_msg = messages[-1].content.lower()
        system_msg = messages[0].content.lower() if len(messages) > 1 else ""
        
        # Detection for Supervisor classification requests
        if "classify" in last_msg or "return only a json object" in last_msg:
            # Smart mock classification
            intent = "Unknown"
            if any(x in last_msg for x in ["leave", "policy", "payroll", "hr"]): intent = "HR"
            elif any(x in last_msg for x in ["laptop", "software", "ticket", "password", "it"]): intent = "IT"
            elif any(x in last_msg for x in ["reimbursement", "finance", "salary"]): intent = "Finance"
            
            response = json.dumps({"intent": intent, "confidence": 0.95})
        
        # Simple domain-specific logic to simulate orchestrated intent
        elif any(x in last_msg for x in ["hi", "hello", "hey"]):
            response = "Hello! I am your Enterprise Service Assistant. How can I help you today? (System: Running in Mock Mode)"
        elif "it" in last_msg or "password" in last_msg or "software" in last_msg:
            response = "I have recognized an IT-related request. Redirecting to IT Support protocols. (Mock Response)"
        elif "hr" in last_msg or "leave" in last_msg or "payroll" in last_msg or "policy" in last_msg:
            response = "Accessing Human Resources knowledge base for your inquiry. (Mock Response)"
        elif "finance" in last_msg or "tax" in last_msg or "salary" in last_msg:
            response = "Connecting to Financial Operations agent for processing. (Mock Response)"
        else:
            response = "I have processed your request through our multi-agent cluster. Everything looks good! (Mock Response)"
            
        message = AIMessage(content=response)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "mock"

def get_llm(node_type="domain_agent", config=None):
    """
    Returns the configured LLM. Supports runtime configuration overrides.
    Falls back to MockLLM if no valid API key is found.
    """
    provider = (config or {}).get("provider") or ACTIVE_PROVIDER
    model = (config or {}).get("model") or MODEL_ROUTING.get(node_type, "gpt-4o-mini")
    api_key = (config or {}).get("api_key")

    if not api_key:
        if provider == "openai": api_key = OPENAI_API_KEY
        elif provider == "groq": api_key = GROQ_API_KEY
        elif provider == "openrouter": api_key = OPENROUTER_API_KEY
        elif provider == "local": api_key = "none"

    # Use MockLLM if key is a placeholder or missing
    if (not api_key or api_key == "sk-placeholder") and provider != "local":
        print(f"[LLM] Using MockLLM for {node_type} (No Key Found)")
        return MockLLM()

    if provider == "openai":
        return ChatOpenAI(api_key=api_key, model=model, temperature=0)
    
    elif provider == "groq":
        return ChatOpenAI(api_key=api_key, model=model, base_url="https://api.groq.com/openai/v1", temperature=0)
    
    elif provider == "openrouter":
        return ChatOpenAI(api_key=api_key, model=model, base_url="https://openrouter.ai/api/v1", temperature=0)
    
    elif provider == "local":
        return ChatOpenAI(api_key="none", model=model, base_url=LOCAL_LLM_URL, temperature=0)
    
    return MockLLM()

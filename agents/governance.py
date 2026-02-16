from ai_service import get_llm
from graph.state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
import json

class GovernanceAgent:
    """
    Acts as a Privacy Shield and Policy Guardrail.
    Filters PII and ensures queries comply with corporate safety standards.
    """
    def __init__(self):
        pass

    def filter_pii(self, state: AgentState) -> dict:
        """
        Scans messages for PII and redacts them before further processing.
        """
        config = state.get("config_override", {})
        llm = get_llm(node_type="privacy", config=config)
        last_message = state['messages'][-1].content
        
        prompt = f"""
        Act as a PII Redactor for an enterprise service desk.
        Analyze the following text and redact any sensitive information (Emails, Passwords, SSNs, Credit Card numbers).
        Replace sensitive data with [REDACTED_TYPE].
        If no sensitive data is found, return the text exactly as is.

        Text: "{last_message}"

        Return ONLY the redacted text.
        """
        
        response = llm.invoke([SystemMessage(content="You are a privacy shield."), HumanMessage(content=prompt)])
        
        print(f"[NODE] Privacy Shield: Scanned and processed query.")
        
        # We replace the content of the message in the graph flow
        redacted_content = response.content.strip()
        
        return {
            "messages": [HumanMessage(content=redacted_content)]
        }

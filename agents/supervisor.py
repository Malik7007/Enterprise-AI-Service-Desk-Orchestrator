import json
from langchain_core.messages import SystemMessage, HumanMessage
from ai_service import get_llm
from graph.state import AgentState

class SupervisorAgent:
    """
    Orchestrates the workflow by classifying user intent and scoring confidence.
    Acts as the entry point for all user queries.
    """
    def __init__(self):
        pass

    def classify(self, state: AgentState) -> dict:
        """
        Classifies the user intent into HR, IT, Finance, Multi-intent, or Unknown.
        """
        last_message = state['messages'][-1].content
        
        # Immediate short-circuit for simple greetings
        if any(x in last_message.lower() for x in ["hi", "hello", "hey"]):
            print(f"[NODE] Supervisor handled greeting.")
            return {
                "intent": "Greeting",
                "confidence": 1.0,
                "response": "Hello! I am your Enterprise Service Assistant. How can I help you today?",
                "all_responses": ["Assistant: Hello! I am your Enterprise Service Assistant. How can I help you today?"]
            }

        config = state.get("config_override", {})
        llm = get_llm(node_type="supervisor", config=config)
        
        prompt = f"""
        Analyze the following user query for an enterprise service desk and classify it.
        
        Intents:
        - HR: Questions about leave, payroll, policy, benefits.
        - IT: Technical issues, software, hardware, tickets.
        - Finance: Reimbursements, expenses, claims.
        - Multi-intent: The query contains more than one request (e.g., IT issue AND HR question).
        - Unknown: Anything else.

        Query: "{last_message}"

        Return ONLY a JSON object:
        {{
            "intent": "HR" | "IT" | "Finance" | "Multi-intent" | "Unknown",
            "confidence": float (0.0 to 1.0)
        }}
        """
        
        response = llm.invoke([SystemMessage(content="You are a supervisor for an enterprise service desk."), HumanMessage(content=prompt)])
        
        try:
            # Handle potential JSON parsing errors
            content = response.content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            print(f"[NODE] Supervisor classified intent: {result.get('intent')} with confidence {result.get('confidence')}")
            return {
                "intent": result.get("intent"),
                "confidence": result.get("confidence")
            }
        except Exception as e:
            print(f"[RECOVER] Supervisor parsing failed: {e}")
            return {"intent": "Unknown", "confidence": 0.0}

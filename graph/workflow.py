from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import AgentState
from agents.supervisor import SupervisorAgent
from agents.hr_agent import HRAgent
from agents.it_agent import ITAgent
from agents.finance_agent import FinanceAgent
from agents.planner import PlannerAgent
from agents.governance import GovernanceAgent
from config import CONFIDENCE_THRESHOLD
import sqlite3

# Initialize Agents
governance = GovernanceAgent()
supervisor = SupervisorAgent()
hr_agent = HRAgent()
it_agent = ITAgent()
finance_agent = FinanceAgent()
planner = PlannerAgent()

def human_escalation(state: AgentState) -> dict:
    """
    Escalation node for low confidence or unknown intents.
    This node can be manually reviewed in LangGraph via interrupts.
    """
    msg = "Your request has been escalated to a human support representative."
    print(f"[NODE] Escalation triggered.")
    return {
        "response": msg,
        "escalation": True,
        "all_responses": [f"System: {msg}"]
    }

def consume_task(state: AgentState) -> dict:
    """
    Consumes the first task from the list and prepares state for it.
    """
    tasks = state.get("tasks", [])
    if not tasks:
        return {}
    
    remaining_tasks = tasks[1:]
    if not remaining_tasks:
        return {"tasks": [], "current_task": None}
    
    next_task = remaining_tasks[0]
    return {
        "tasks": remaining_tasks,
        "current_task": next_task['task'],
        "intent": next_task['agent']
    }

def merge_responses(state: AgentState) -> dict:
    """
    Merges responses from multiple agents into one coherent final response.
    """
    all_res = state.get("all_responses", [])
    final_response = "\n\n".join(all_res)
    print(f"[NODE] Merged final response.")
    return {"response": final_response}

def router_logic(state: AgentState):
    """
    Core routing logic based on supervisor classification.
    """
    intent = state.get("intent")
    confidence = state.get("confidence", 0.0)
    
    if confidence < CONFIDENCE_THRESHOLD:
        return "escalation"
    
    if intent == "HR":
        return "hr"
    elif intent == "IT":
        return "it"
    elif intent == "Finance":
        return "finance"
    elif intent == "Multi-intent":
        return "planner"
    else:
        return "escalation"

def next_step_router(state: AgentState):
    """
    Determines if there are more tasks to process or if we should finish.
    """
    tasks = state.get("tasks", [])
    if tasks and len(tasks) > 0:
        return state.get("intent").lower()
    return "merge"

def build_workflow():
    """
    Updated LangGraph workflow with:
    1. Privacy Shield (PII Filtering)
    2. Persistence (SqliteSaver)
    3. Human-In-The-Loop (Interrupts)
    """
    # 1. Memory for Persistence (Transient)
    memory = MemorySaver()
    
    workflow = StateGraph(AgentState)

    # Define Nodes
    workflow.add_node("privacy_shield", governance.filter_pii)
    workflow.add_node("supervisor", supervisor.classify)
    workflow.add_node("hr", hr_agent.execute)
    workflow.add_node("it", it_agent.execute)
    workflow.add_node("finance", finance_agent.execute)
    workflow.add_node("planner", planner.plan)
    workflow.add_node("consume_task", consume_task)
    workflow.add_node("escalation", human_escalation)
    workflow.add_node("merge", merge_responses)

    # Define Connectivity
    workflow.set_entry_point("privacy_shield")
    workflow.add_edge("privacy_shield", "supervisor")

    # Routing from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        router_logic,
        {
            "hr": "hr",
            "it": "it",
            "finance": "finance",
            "planner": "planner",
            "escalation": "escalation"
        }
    )

    workflow.add_edge("hr", "consume_task")
    workflow.add_edge("it", "consume_task")
    workflow.add_edge("finance", "consume_task")

    workflow.add_conditional_edges(
        "consume_task",
        next_step_router,
        {
            "hr": "hr",
            "it": "it",
            "finance": "finance",
            "merge": "merge"
        }
    )

    def planner_routing(state: AgentState):
        intent = state.get("intent", "").lower()
        if intent in ["hr", "it", "finance"]:
            return intent
        return "escalation"
    
    workflow.add_conditional_edges("planner", planner_routing, {"hr": "hr", "it": "it", "finance": "finance"})

    workflow.add_edge("merge", END)
    workflow.add_edge("escalation", END)

    # Compile with checkpointer and human-in-the-loop interrupt
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["escalation"]
    )

def reindex_domain(domain: str):
    """
    Manually triggers a re-indexing of a domain's vector store.
    """
    if domain.upper() == "IT":
        it_agent.vector_store.initialize_store()
    elif domain.upper() == "HR":
        hr_agent.vector_store.initialize_store()
    elif domain.upper() == "FINANCE":
        finance_agent.vector_store.initialize_store()
    print(f"[SYSTEM] Re-indexed {domain} domain.")

# Singleton app instance
app = build_workflow()

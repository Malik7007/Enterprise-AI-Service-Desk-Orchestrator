import json
from langchain_core.messages import SystemMessage, HumanMessage
from ai_service import get_llm
from graph.state import AgentState

class PlannerAgent:
    """
    Handles complex, multi-intent queries by decomposing them into sequential tasks.
    Enables the orchestrator to handle queries like "My laptop is broken and I need leave info".
    """
    def __init__(self):
        pass

    def plan(self, state: AgentState) -> dict:
        """
        Splits the user query into a list of specific sub-tasks with assigned agents.
        @param state - Current graph state
        @returns List of tasks for sequential execution
        """
        config = state.get("config_override", {})
        llm = get_llm(node_type="planner", config=config)
        query = state['messages'][-1].content
        
        prompt = f"""
        Break the following multi-intent user query into a list of tasks.
        Each task must specify the target agent: HR, IT, or Finance.

        Query: "{query}"

        Return ONLY a JSON array of objects:
        [
            {{"agent": "IT", "task": "troubleshoot laptop"}},
            {{"agent": "Finance", "task": "reimbursement procedure"}}
        ]
        """
        
        response = llm.invoke([SystemMessage(content="You are a task planner for a service desk."), HumanMessage(content=prompt)])
        
        try:
            content = response.content.replace("```json", "").replace("```", "").strip()
            tasks_list = json.loads(content)
            print(f"[NODE] Planner created {len(tasks_list)} tasks: {tasks_list}")
            
            # We store tasks in state. The graph will consume them one by one.
            return {
                "tasks": tasks_list,
                "current_task": tasks_list[0]['task'] if tasks_list else None,
                "intent": tasks_list[0]['agent'] if tasks_list else "Unknown" # Redirect to first agent
            }
        except Exception as e:
            print(f"[RECOVER] Planner failed: {e}")
            return {"tasks": [], "intent": "Unknown"}

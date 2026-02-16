from langchain_core.messages import SystemMessage, HumanMessage
from ai_service import get_llm
from graph.state import AgentState
from rag.vectorstore import VectorStoreManager
from tools.finance_tool import validate_reimbursement
from config import DATA_DIR
import os
import re

class FinanceAgent:
    """
    Handles financial queries and reimbursement validations.
    """
    def __init__(self):
        self.vector_store = VectorStoreManager("Finance", os.path.join(DATA_DIR, "finance_docs"))

    def execute(self, state: AgentState) -> dict:
        """
        Handles reimbursement and general finance questions.
        @param state - Current graph state
        @returns Updated state with Finance response
        """
        config = state.get("config_override", {})
        llm = get_llm(node_type="domain_agent", config=config)
        query = state.get("current_task") or state['messages'][-1].content
        
        # RAG Step
        docs = self.vector_store.search(query)
        context = "\n\n".join([d.page_content for d in docs])
        
        # Check for reimbursement validation trigger
        # Simple heuristic: if 'reimburse' and an amount (number) are present
        amount_match = re.search(r'(\d+)', query)
        validation_output = ""
        if "reimbursement" in query.lower() and amount_match:
            amount = float(amount_match.group(1))
            validation_output = f"\n\n[Validation] {validate_reimbursement.invoke({'amount': amount, 'category': 'General Expense'})}"

        prompt = f"""
        You are a Finance Specialist. Use the context to answer questions about reimbursements and bonuses.
        
        Context:
        {context}
        
        User Query: {query}
        """
        
        response = llm.invoke([SystemMessage(content="You are helpful Finance agent."), HumanMessage(content=prompt)])
        
        final_response = response.content + validation_output
        print(f"[NODE] Finance Agent generated response for: {query[:50]}...")

        return {
            "response": final_response,
            "all_responses": [f"Finance: {final_response}"]
        }

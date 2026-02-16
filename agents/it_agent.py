from langchain_core.messages import SystemMessage, HumanMessage
from ai_service import get_llm
from graph.state import AgentState
from rag.vectorstore import VectorStoreManager
from tools.ticket_tool import create_ticket
from config import DATA_DIR
import os

class ITAgent:
    """
    Handles IT support queries. Can create tickets if troubleshooting fails.
    """
    def __init__(self):
        self.vector_store = VectorStoreManager("IT", os.path.join(DATA_DIR, "it_docs"))

    def execute(self, state: AgentState) -> dict:
        """
        Retrieves IT docs and attempts to solve or escalate via ticket.
        @param state - Current graph state
        @returns Updated state with IT response and potential ticket ID
        """
        config = state.get("config_override", {})
        llm = get_llm(node_type="domain_agent", config=config)
        query = state.get("current_task") or state['messages'][-1].content
        
        # RAG Step
        docs = self.vector_store.search(query)
        context = "\n\n".join([d.page_content for d in docs])
        
        prompt = f"""
        You are an IT Support Agent. Use the context to solve the user's technical issue.
        If a ticket needs to be created, state clearly: "I will create a ticket for you."
        
        Context:
        {context}
        
        User Query: {query}
        """
        
        response = llm.invoke([SystemMessage(content="You are helpful IT agent."), HumanMessage(content=prompt)])
        
        ticket_id = state.get("ticket_id")
        if "create a ticket" in response.content.lower():
            # Tool call (manual simulation for this node, or could use LangChain tool binding)
            ticket_id = create_ticket.invoke(query)
            response_text = f"{response.content}\n\n[System Output] Ticket ID: {ticket_id}"
        else:
            response_text = response.content

        print(f"[NODE] IT Agent generated response and ticket: {ticket_id}")
        
        return {
            "response": response_text,
            "ticket_id": ticket_id,
            "all_responses": [f"IT: {response_text}"]
        }

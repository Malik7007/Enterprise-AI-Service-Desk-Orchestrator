from langchain_core.messages import SystemMessage, HumanMessage
from ai_service import get_llm
from graph.state import AgentState
from rag.vectorstore import VectorStoreManager
from config import DATA_DIR
import os

class HRAgent:
    """
    Handles HR-related queries using domain-specific RAG.
    """
    def __init__(self):
        self.vector_store = VectorStoreManager("HR", os.path.join(DATA_DIR, "hr_docs"))

    def execute(self, state: AgentState) -> dict:
        """
        Retrieves HR documents and generates a grounded response.
        @param state - Current graph state
        @returns Updated state with HR response
        """
        config = state.get("config_override", {})
        llm = get_llm(node_type="domain_agent", config=config)
        # Multi-intent check: if we are in a subtask, use that as query
        query = state.get("current_task") or state['messages'][-1].content
        
        # RAG Step
        docs = self.vector_store.search(query)
        context = "\n\n".join([d.page_content for d in docs])
        
        prompt = f"""
        You are an HR Specialist. Use the following policy documents to answer the query.
        If the answer is not in the documents, say you don't know.
        
        Context:
        {context}
        
        User Query: {query}
        """
        
        response = llm.invoke([SystemMessage(content="You are helpful HR agent."), HumanMessage(content=prompt)])
        
        print(f"[NODE] HR Agent generated response for: {query[:50]}...")
        
        return {
            "response": response.content,
            "all_responses": [f"HR: {response.content}"]
        }

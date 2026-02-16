from graph.workflow import app as graph_app
from langchain_core.messages import HumanMessage
import json

def run_test(query: str):
    print(f"\n{'='*50}")
    print(f"USER QUERY: {query}")
    print(f"{'='*50}")
    
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "all_responses": []
    }
    
    # Run the graph
    result = graph_app.invoke(initial_state)
    
    print(f"\nFINAL OUTPUT:")
    print(f"Response: {result.get('response')}")
    print(f"Ticket ID: {result.get('ticket_id')}")
    print(f"Escalation: {result.get('escalation')}")
    print(f"Intent: {result.get('intent')}")
    print(f"Confidence: {result.get('confidence')}")

if __name__ == "__main__":
    # Test cases
    scenarios = [
        "Can I carry forward unused leave?",
        "My laptop is damaged and I want reimbursement."
    ]
    
    for s in scenarios:
        try:
            run_test(s)
        except Exception as e:
            print(f"Error running test for '{s}': {e}")

import random
import time
from langchain_core.tools import tool

@tool
def create_ticket(issue_desc: str):
    """
    Simulates a connection to Jira/ServiceNow to create a support ticket.
    Enterprise Ready: Includes mock latency and structured metadata.
    """
    # 🧪 Enterprise Simulation: Real APIs have latency
    time.sleep(1.2) 
    
    prefixes = ["JIRA", "SNOW", "SVC"]
    ticket_id = f"{random.choice(prefixes)}-{random.randint(1000, 9999)}"
    
    return {
        "id": ticket_id,
        "status": "QUEUED",
        "priority": "MEDIUM",
        "cluster_node": "AWS-US-EAST-1",
        "description": issue_desc[:50] + "..."
    }

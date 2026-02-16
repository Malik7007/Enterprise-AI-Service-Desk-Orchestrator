import random
import time
from langchain.tools import tool

@tool
def create_ticket(issue_description: str) -> str:
    """
    Creates an IT support ticket in the internal Jira/ServiceNow system.
    @param issue_description - Detailed description of the problem
    @returns A formal Ticket ID with status confirmation
    """
    # Simulate API Latency for realism
    time.sleep(1.2)
    
    # Mock ticket creation logic with standard corporate format
    ticket_id = f"SRV-{random.randint(100000, 999999)}"
    print(f"[API CALL] POST /v1/tickets -> {ticket_id}")
    
    return ticket_id

from typing import Optional
from langchain.tools import tool

@tool
def validate_reimbursement(amount: float, category: str) -> str:
    """
    Validates a reimbursement claim against corporate policy.
    @param amount - The currency amount to be reimbursed
    @param category - The type of expense (e.g., 'Travel', 'Laptop Repair')
    @returns Validation result string
    """
    # Mock validation logic
    if amount > 5000:
        return f"Denied: {category} claim of {amount} exceeds immediate approval limit. Escalating to Finance Manager."
    
    return f"Approved: {category} claim for {amount} is within corporate limits."

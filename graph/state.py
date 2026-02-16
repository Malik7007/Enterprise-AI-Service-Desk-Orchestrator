from typing import List, Optional, TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    State definition for the LangGraph workflow.
    Ensures data persistence and communication between agent nodes.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    intent: Optional[str]
    confidence: Optional[float]
    tasks: Optional[List[str]]
    current_task: Optional[str]
    ticket_id: Optional[str]
    response: Optional[str]
    escalation: Optional[bool]
    all_responses: Annotated[List[str], operator.add] # Used to merge multi-intent results

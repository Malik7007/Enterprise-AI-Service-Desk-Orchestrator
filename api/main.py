from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
from langchain_core.messages import HumanMessage
from graph.workflow import app as graph_app
import uuid
import json
import asyncio

app = FastAPI(title="Enterprise AI Service Desk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat_stream(request: ChatRequest):
    """
    Advanced Streaming Endpoint.
    Uses Server-Sent Events (SSE) to stream graph execution nodes and final response.
    Enables persistent conversation memory via thread_id and LangGraph Checkpointers.
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    async def event_generator() -> AsyncGenerator[dict, None]:
        # Initial status
        print(f"[API] Chat request received. Provider: {request.provider}, Model: {request.model}")
        yield {"event": "status", "data": json.dumps({"node": "init", "thread_id": thread_id, "provider": request.provider, "model": request.model})}
        
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "all_responses": [],
            "config_override": {
                "provider": request.provider,
                "model": request.model,
                "api_key": request.api_key
            }
        }
        
        # We use astream to get updates for each node execution
        try:
            async for event in graph_app.astream(initial_state, config, stream_mode="updates"):
                node_name = list(event.keys())[0] if event else "unknown"
                node_data = event[node_name]
                
                # Filter what to send back for security/cleanliness
                update = {
                    "node": node_name,
                    "intent": node_data.get("intent"),
                    "confidence": node_data.get("confidence"),
                    "ticket_id": node_data.get("ticket_id"),
                    "escalation": node_data.get("escalation")
                }
                
                yield {"event": "node_update", "data": json.dumps(update)}
                
                # Check for completion
                if "response" in node_data:
                    yield {"event": "final_response", "data": json.dumps({
                        "response": node_data["response"],
                        "ticket_id": node_data.get("ticket_id"),
                        "escalation": node_data.get("escalation")
                    })}

        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())

# Endpoint for manual human approval (HITL Gap)
@app.post("/approve/{thread_id}")
async def approve_step(thread_id: str):
    """
    Resumes a paused graph execution (e.g., after a human escalation trigger).
    """
    config = {"configurable": {"thread_id": thread_id}}
    try:
        # Pass None to resume after interrupt
        result = graph_app.invoke(None, config)
        return {"status": "resumed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

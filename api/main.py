from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
from langchain_core.messages import HumanMessage
from graph.workflow import app as graph_app, reindex_domain
import uuid
import json
import asyncio
import os
import shutil
import requests

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

class ModelFetchRequest(BaseModel):
    provider: str
    api_key: str
    base_url: Optional[str] = None

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/fetch-models")
async def fetch_models(request: ModelFetchRequest):
    """
    Dynamically fetches models from the chosen provider using the user's API key.
    """
    try:
        if request.provider == "openai":
            headers = {"Authorization": f"Bearer {request.api_key}"}
            res = requests.get("https://api.openai.com/v1/models", headers=headers)
            models = [m["id"] for m in res.json().get("data", []) if "gpt" in m["id"]]
            return {"models": sorted(models)}
        
        elif request.provider == "groq":
            headers = {"Authorization": f"Bearer {request.api_key}"}
            res = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
            models = [m["id"] for m in res.json().get("data", [])]
            return {"models": sorted(models)}
            
        elif request.provider == "openrouter":
            headers = {"Authorization": f"Bearer {request.api_key}"}
            res = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
            # OpenRouter has MANY models, we filter for common ones
            data = res.json().get("data", [])
            models = [m["id"] for m in data if any(x in m["id"] for x in ["claude", "gpt", "gemini", "llama"])]
            return {"models": sorted(models)}

        elif request.provider == "local":
            url = request.base_url or "http://localhost:11434"
            res = requests.get(f"{url}/api/tags")
            models = [m["name"] for m in res.json().get("models", [])]
            return {"models": sorted(models)}

        return {"models": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), domain: str = Form(...)):
    """
    Saves uploaded files to the domain-specific RAG directory.
    """
    base_dir = os.path.join(os.getcwd(), "data", f"{domain.lower()}_docs")
    os.makedirs(base_dir, exist_ok=True)
    
    file_path = os.path.join(base_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Trigger RAG re-indexing for the specific domain
        reindex_domain(domain)
        
        return {"status": "success", "filename": file.filename, "domain": domain}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_stream(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    async def event_generator() -> AsyncGenerator[dict, None]:
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
        
        try:
            async for event in graph_app.astream(initial_state, config, stream_mode="updates"):
                node_name = list(event.keys())[0] if event else "unknown"
                node_data = event[node_name]
                
                update = {
                    "node": node_name,
                    "intent": node_data.get("intent"),
                    "confidence": node_data.get("confidence"),
                    "ticket_id": node_data.get("ticket_id"),
                    "escalation": node_data.get("escalation")
                }
                
                yield {"event": "node_update", "data": json.dumps(update)}
                
                if "response" in node_data:
                    yield {"event": "final_response", "data": json.dumps({
                        "response": node_data["response"],
                        "ticket_id": node_data.get("ticket_id"),
                        "escalation": node_data.get("escalation")
                    })}

        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())

@app.post("/approve/{thread_id}")
async def approve_step(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        result = graph_app.invoke(None, config)
        return {"status": "resumed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

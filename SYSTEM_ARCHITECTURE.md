# System Architecture: Enterprise AI Service Desk (Orchestrator)

## 📌 Executive Summary
A **Multi-Agent Cognitive Framework** designed to handle complex enterprise service requests (IT, HR, Finance) through a centralized, persistent graph-based workflow.

It uses **LangGraph** to model the decision-making process as a directed cyclic graph (DCG), allowing agents to:
1.  Verify their own outputs.
2.  Decompose complex tasks into sub-tasks (Planning).
3.  Route requests to specialized domain experts.
4.  Persist state across sessions (SQLite Checkpoints).

---

## 🏗️ High-Level Topology

```mermaid
graph TD
    User([User Request]) --> PrivacyShield[🛡️ PII Scrubber]
    PrivacyShield --> Supervisor[🧠 Supervisor Agent]

    subgraph "Domain Clusters"
        Supervisor -- "Simple Intent" --> HRAgent[HR Expert (RAG)]
        Supervisor -- "Simple Intent" --> ITAgent[IT Expert (Tools)]
        Supervisor -- "Simple Intent" --> FinAgent[Finance Expert]
    end

    subgraph "Complex Planning"
        Supervisor -- "Multi-Step" --> Planner[📝 Task Planner]
        Planner --> TaskQueue[(Task Queue)]
        TaskQueue --> Consumer[Processor]
        Consumer --> HRAgent
        Consumer --> ITAgent
        Consumer --> FinAgent
    end

    HRAgent --> Merger[Response Synthesizer]
    ITAgent --> Merger
    FinAgent --> Merger

    Merger --> AuditLog[(Audit DB)]
    AuditLog --> UI([Frontend Stream])
```

## 🧩 Core Components

### 1. The Supervisor (Router)
The **Supervisor** is the cognitive router. It uses a **Classification Prompt** to determine if the user's intent is simple (one domain) or complex (multi-step).
*   **Simple**: "Reset my password" -> Routes to IT.
*   **Complex**: "My laptop broke and I need to claim inconsistent leave" -> Routes to Planner.

### 2. The Planner (Decomposer)
For multi-intent queries, the **Planner Agent** breaks the request down into a JSON list of tasks:
```json
[
  {"agent": "IT", "task": "Create a ticket for broken laptop"},
  {"agent": "HR", "task": "Check leave policy for inconsistent leave"}
]
```
These tasks are pushed to the **State** and consumed sequentially.

### 3. Domain Agents (RAG & Tools)
Each domain agent is specialized:
*   **IT Agent**: Has access to `create_ticket` tool and IT Knowledge Base.
*   **HR Agent**: Has access to `search_policy` tool (RAG).
*   **Finance Agent**: Has access to `validate_expense` logic.

### 4. Persistence Layer (SQLite)
We use `AsyncSqliteSaver` (or standard `SqliteSaver` in synchronous mode) to checkpoint the graph state after every node execution.
*   **Benefit**: If the server crashes, the conversation resumes exactly where it left off.
*   **Benefit**: Allows for "Time Travel" debugging (inspecting past states).

### 5. Frontend (React + SSE)
The UI is a **Real-Time Dashboard** that visualizes the thought process.
*   **Token Streaming**: Uses Server-Sent Events (SSE) to stream tokens as they are generated.
*   **Node Updates**: The backend pushes "Node Active: HR" events, which the frontend uses to light up the corresponding agent avatar.

## 🛡️ Governance Layer

### Privacy Shield
A dedicated node that runs *before* the Supervisor. It uses regex and lightweight NLP to redact:
*   Email addresses
*   Phone numbers
*   SSN/Credit Card patterns

### Audit Logging
Every final response is written to `audit_log.db` with:
*   `thread_id`: To trace the full conversation history.
*   `provider`: Which LLM was used (OpenAI, Groq, Local).
*   `timestamp`: When the action occurred.

## 📂 Directory Structure Explained

*   **`agents/`**: Contains the logic for each agent (Supervisor, Planner, IT, HR, Finance).
*   **`graph/`**: Defines the LangGraph workflow (`workflow.py`) and state schema (`state.py`).
*   **`rag/`**: Managing Vector Stores (FAISS) and Document Loaders.
*   **`tools/`**: Python functions exposed to the LLM as tools (e.g., `ticket_tool.py`).
*   **`api/`**: FastAPI endpoints that expose the graph to the frontend.

## 🚀 deployment

The system is container-ready but currently configured for a monolithic local deployment via `run.ps1`.
Future roadmap includes Dockerizing each agent as a microservice.

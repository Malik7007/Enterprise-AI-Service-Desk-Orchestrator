# Enterprise AI Service Desk Orchestrator (Alpha-V2)

🚀 **Production-grade Multi-Agent AI System** built with **LangGraph**, **LangChain**, and **FastAPI**.

This system is an advanced demonstration of **Agentic AI Orchestration**, featuring a self-correcting multi-agent cluster that handles Enterprise IT, HR, and Finance service requests with built-in governance and human-in-the-loop fallback.

## 🏗️ Technical Architecture

The system implements a **Decentralized Cognitive Architecture**:

1.  **Privacy Shield (Governance)**: The first line of defense. Scans and redacts PII/Sensitive data before it enters the LLM reasoning cycle.
2.  **Supervisor (Cognitive Router)**: Classifies user intent and assigns confidence scores. It selects the optimal domain agent or triggers the Planner.
3.  **Task Planner (Complexity Handler)**: For multi-step queries like *"My laptop is broken and I'm on leave"*, the Planner decomposes the prompt into discrete task objects for sequential processing.
4.  **Domain Clusters (Isolated RAG)**: 
    *   **IT Agent**: Troubleshoots hardware/software using its specific knowledge base and creates tickets via tools.
    *   **HR Agent**: Grounded in corporate policy docs for leave, payroll, and benefits.
    *   **Finance Agent**: Validates reimbursements and provides financial policy guidance.
5.  **Execution Persistence**: Uses LangGraph checkpoints to maintain conversation state and handle human interrupts (HITL).

## 🧩 Premium Features (Alpha-V2)

*   **Runtime AI Gateway**: Configure API keys (OpenAI, Groq, OpenRouter) or Local Ollama endpoints directly in the UI without restarting the cluster.
*   **Live Orchestration Telemetry**: A real-time execution console that shows the visual "handover" between agents as they reason through your request.
*   **Knowledge Base Management**: Management UI for indexing local document assets (PDF/DOCX) into the vector store.
*   **Glassmorphism UI**: A high-fidelity "Control Center" dashboard built with React, Framer Motion, and Tailwind CSS v4.
*   **Local Intelligence Integration**: Verified support for **Ollama** (Llama3, Mistral) for 100% private local orchestration.

## 🚀 Quick Start (One Command)

The entire cluster (Backend API, Frontend UI, and Python Venv) can be launched with a single script:

```powershell
./run.ps1
```

### Manual Setup

**1. Backend (Python 3.10+):**
```bash
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
python api/main.py
```

**2. Frontend (Node 18+):**
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```text
enterprise_ai_service_desk/
│
├── agents/         # LLM logic for Supervisor, Planner, and Domain experts
├── api/            # FastAPI endpoints & SSE streaming implementation
├── graph/          # LangGraph state management & workflow connectivity
├── rag/            # Vector store management with Semantic Chunking
├── tools/          # Functional tools (IT Ticketing, Finance Validation)
├── data/           # Mock Enterprise knowledge base (Markdown/PDF)
├── frontend/       # React SPA with advanced orchestration visualizer
├── config.py       # Global cluster settings
└── run.ps1         # Unified startup orchestrator
```

## 🧠 Why this Architecture?

*   **LangGraph over Chains**: Standard LLM chains are linear. LangGraph allows for **cycles** and **looping logic**, enabling the agents to verify their own work or ask for clarification.
*   **Isolated Knowledge Domains**: Prevents "Knowledge Leakage" where an agent might hallucinate HR policy into an IT ticket.
*   **Enterprise Governance**: Mandatory PII filtering and sub-threshold confidence detection ensure high-stakes decisions always get human oversight.

---
**Developer:** Arfan (AI/ML Engineer)  
**Email:** arfan.software.engineer@gmail.com  
**Vision:** Towards Autonomous Enterprise Operations.

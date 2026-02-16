# Enterprise AI Service Desk Orchestrator

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10+-blue.svg) ![React](https://img.shields.io/badge/react-18-blue.svg) ![LangGraph](https://img.shields.io/badge/LangGraph-0.1-orange.svg)

**Production-Grade Multi-Agent System** for Enterprise IT, HR, and Finance operations. Built with a decentralized cognitive architecture to handle complex, multi-step requests with privacy, governance, and persistence as first-class citizens.

## 🚀 Key Capabilities

*   **🛡️ Privacy First**: Middleware intercepts all prompts to redact PII (Personally Identifiable Information) before it touches the LLM.
*   **🧠 Cognitive Router**: A Supervisor Agent classifies intent and routes queries to specialized domain experts (IT, HR, Finance) or a Task Planner for complex workflows.
*   **💾 Persistent Memory**: Uses SQLite checkpoints to maintain conversation state across sessions and server restarts.
*   **⚡ True Streaming**: Granular token-by-token streaming for a responsive "typing" feel, even during complex RAG operations.
*   **📂 Enterprise RAG**: Ingests PDF, DOCX, and Markdown files into domain-specific vector stores (FAISS) for grounded answers.
*   **🔧 Auditable Actions**: All agent decisions and tool outputs are logged to a tamper-evident audit database (`audit_log.db`).

## 🏗️ Quick Start

### Prerequisites
*   **Python 3.10+**
*   **Node.js 18+**
*   (Optional) API Keys for OpenAI/Groq or a local Ollama instance.

### One-Command Launch (Windows/Linx/Mac)
We provide a unified orchestrator script that sets up the environment, installs dependencies, and launches both backend and frontend.

```powershell
./run.ps1
```

### Manual Installation
**Backend**
```bash
python -m venv venv
# On Windows:
./venv/Scripts/activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python api/main.py
```

**Frontend**
```bash
cd frontend
npm install
npm run dev -- --port 3000
```

## 🧩 System Architecture

The system follows a **Hub-and-Spoke** agent topology managed by LangGraph.

1.  **User Request** -> **Privacy Shield** (PII Redaction)
2.  **Supervisor** (Intent Classification)
3.  **Routing**:
    *   *Simple Intent* -> **Domain Agent** (HR/IT/Finance)
    *   *Complex Intent* -> **Planner Agent** -> Decomposes into **Task Queue**
4.  **Execution**:
    *   Agents use **Tools** (e.g., `create_ticket`, `search_knowledge_base`)
    *   Agents use **RAG** (Vector Search)
5.  **Response Synthesis**:
    *   Responses are merged and streamed back to the user via **SSE (Server-Sent Events)**.

See [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) for a deep dive.

## 🛡️ Governance & Compliance

*   **Audit Logging**: Every interaction is recorded in `audit_log.db` with timestamps, provider metadata, and full response content.
*   **Human-in-the-Loop (HITL)**: If the Supervisor confidence score drops below 0.7, the system automatically escalates to a human operator (simulated via interrupt signal).

## 🛠️ Configuration

Edit `config.py` to tune system behavior:

```python
CONFIDENCE_THRESHOLD = 0.7  # Trigger escalation below this
MAX_RECURSION_LIMIT = 20    # Prevent infinite loops in complex plans
```

## 🤝 Contributing

We welcome contributions! Please see `CONTRIBUTING.md` (coming soon) for guidelines.

## 📄 License

MIT License. See `LICENSE` for details.

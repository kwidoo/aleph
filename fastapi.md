# FastAPI API Tasks

These tasks describe the API layer to expose the same functionality found in the agent-based RAG automation system. The API will allow AI assistants, UIs, or CLI clients to interact with the agent system programmatically.

---

## 🔹 Phase 1: Base Setup

- [ ] Setup `FastAPI` project with `uvicorn` for dev server
- [ ] Add middleware for logging, CORS, and error handling
- [ ] Define shared `schemas.py` with Pydantic models
- [ ] Load `.env` using `python-dotenv`
- [ ] Define `settings.py` using `BaseSettings` for config management

---

## 🔹 Phase 2: Project and File API

- [ ] `/projects`:
  - `GET`: List all known projects
  - `POST`: Create new project (with metadata or name)
- [ ] `/projects/{project_id}`:
  - `GET`: Get project details
  - `DELETE`: Remove project

- [ ] `/projects/{project_id}/files`:
  - `GET`: List all files
  - `POST`: Upload file to project
- [ ] `/projects/{project_id}/files/{file_id}`:
  - `GET`: Get file contents
  - `DELETE`: Delete file

---

## 🔹 Phase 3: Agent Execution API

- [ ] `/agents`:
  - `GET`: List available agents (e.g., DesignToComponentAgent, TestAgent)
- [ ] `/agents/{agent_id}/run`:
  - `POST`: Run a specific agent on given input
    - Payload: `{ "project_id": ..., "file_ids": [...], "params": { ... } }`
  - `GET`: Fetch last result or logs from that agent

- [ ] `/agents/{agent_id}/tasks`:
  - `GET`: List previously executed tasks for an agent
  - `POST`: Submit a new task manually

---

## 🔹 Phase 4: Embeddings & Search API

- [ ] `/projects/{project_id}/search`:
  - `POST`: Perform semantic search over indexed content
  - Payload: `{ "query": "..." }`

- [ ] `/projects/{project_id}/embedding-status`:
  - `GET`: Check if embeddings are up to date
  - `POST`: Trigger (re)embedding for project

---

## 🔹 Phase 5: Automation Control API

- [ ] `/workflows`:
  - `POST`: Run predefined workflows (e.g., “analyze + test + review”)
  - `GET`: List all workflows

- [ ] `/logs`:
  - `GET`: Return logs for agents, tasks, or the system

---

## 🔹 Phase 6: Admin/Utility Endpoints

- [ ] `/status`:
  - `GET`: Healthcheck/status of RAG/LLM subsystems
- [ ] `/config`:
  - `GET/POST`: Read or update runtime config

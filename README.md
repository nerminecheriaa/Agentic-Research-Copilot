# Agentic Research Copilot — Corrective RAG Multi-Agent

An agent that answers technical questions via RAG, self-corrects (grading retrieved documents, query reformulation/web search if needed), and has its response verified by a critic agent before delivery.

Stack: FastAPI (SSE) · LangGraph · Qdrant · RAGAS · Next.js · Docker · GitHub Actions · LangSmith.

## Run Locally

```bash
cp .env.example .env   # then fill in the API keys
docker compose up --build
```
- Backend : http://localhost:8000/health
- Qdrant dashboard : http://localhost:6333/dashboard

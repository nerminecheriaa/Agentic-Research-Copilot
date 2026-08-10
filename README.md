# Agentic Research Copilot — Corrective RAG Multi-Agent

Agent qui répond à des questions techniques via RAG, s'auto-corrige (grading des
documents récupérés, reformulation/recherche web si besoin) et fait vérifier
sa réponse par un agent critique avant de la livrer.

Stack : FastAPI (SSE) · LangGraph · Qdrant · RAGAS · Next.js · Docker ·
GitHub Actions · LangSmith.

## Lancer en local

```bash
cp .env.example .env   # puis remplir les clés API
docker compose up --build
```

- Backend : http://localhost:8000/health
- Qdrant dashboard : http://localhost:6333/dashboard

# Agentic Research Copilot — Corrective RAG Multi-Agent

Agent qui répond à des questions techniques via RAG, s'auto-corrige (grading des
documents récupérés, reformulation/recherche web si besoin) et fait vérifier
sa réponse par un agent critique avant de la livrer.

Stack : FastAPI (SSE) · LangGraph · Qdrant · RAGAS · Next.js · Docker ·
GitHub Actions · LangSmith.

## Avancement

- [x] Semaine 1 — Setup Qdrant (Docker) + squelette FastAPI
- [ ] Semaine 1 — Ingestion du corpus
- [ ] Semaine 1 — Graphe LangGraph minimal (retrieve → generate)
- [ ] Semaine 1 — Grading + boucle de correction (rewrite_query + web_search)
- [ ] Semaine 2 — Agent critique + retry borné
- [ ] Semaine 2 — Évaluation RAGAS
- [ ] Semaine 2 — LangSmith
- [ ] Semaine 3 — SSE/WebSocket
- [ ] Semaine 3 — Frontend Next.js
- [ ] Semaine 3 — CI/CD GitHub Actions
- [ ] Semaine 3 — Déploiement cloud (Railway/Fly.io + Vercel)

## Lancer en local

```bash
cp .env.example .env   # puis remplir les clés API
docker compose up --build
```

- Backend : http://localhost:8000/health
- Qdrant dashboard : http://localhost:6333/dashboard

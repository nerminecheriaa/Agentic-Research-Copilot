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

## Lancer en local

```bash
cp .env.example .env   # puis remplir les clés API
docker compose up --build
```

- Backend : http://localhost:8000/health
- Qdrant dashboard : http://localhost:6333/dashboard

## Ingérer le corpus (arXiv)

Depuis `backend/`, avec un venv local (les embeddings tournent en local via FastEmbed,
pas besoin de clé API) :

```bash
cd backend
pip install -r requirements.txt
python -m app.ingestion.fetch_arxiv --query "retrieval augmented generation" --max-results 20
python -m app.ingestion.build_index
```

Adapte `--query` à ton sujet (ex : "corrective RAG", "LLM agents", "multi-agent reasoning").
Qdrant doit tourner (`docker compose up -d qdrant`) et `QDRANT_URL` doit pointer dessus
(`http://localhost:6333` en local hors Docker, `http://qdrant:6333` depuis le conteneur backend).

## Tester le graphe Corrective RAG

```bash
cd backend
py -m app.graph.run "Qu'est-ce que le corrective RAG ?"
```

Nécessite `GROQ_API_KEY` dans `.env` (et `TAVILY_API_KEY` pour le fallback web search,
optionnel — sans elle l'étape web_search est simplement ignorée).

## Évaluer avec RAGAS

```bash
cd backend
py -m eval.run_eval
```

Fait tourner le graphe sur 6 questions de référence (`backend/eval/dataset.json`), calcule
`faithfulness` (la réponse est-elle fondée sur les documents ?) et `answer_relevancy`, et
sauvegarde le détail par question dans `backend/eval/results.csv`.

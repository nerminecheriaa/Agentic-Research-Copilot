from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.chat import router as chat_router
app = FastAPI(title="Agentic Research Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre une fois le frontend déployé
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)

@app.get("/health")
def health():
    return {"status": "ok", "qdrant_collection": settings.qdrant_collection}


# TODO (Semaine 1, étape suivante) :
#   - app/ingestion/ : script de chargement + chunking + embedding du corpus dans Qdrant
#   - app/graph/ : graphe LangGraph (retrieve -> grade -> rewrite/web_search -> generate -> critique)
#   - endpoint /chat en streaming SSE branché sur le graphe

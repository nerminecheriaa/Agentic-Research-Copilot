"""
Endpoint /chat : version synchrone simple. FastAPI exécute automatiquement les
fonctions de route "def" (non-async) dans un threadpool interne — pas besoin de
gérer ça nous-mêmes avec asyncio.to_thread, ce qui élimine une source de bugs.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.graph.build import app_graph

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    grounded: bool
    retries: int


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    initial_state = {
        "question": req.question,
        "search_query": "",
        "documents": [],
        "generation": "",
        "retries": 0,
        "max_retries": 2,
        "grounded": False,
    }
    result = app_graph.invoke(initial_state)
    return ChatResponse(
        answer=result["generation"],
        sources=[d["source"] for d in result["documents"]],
        grounded=result["grounded"],
        retries=result["retries"],
    )

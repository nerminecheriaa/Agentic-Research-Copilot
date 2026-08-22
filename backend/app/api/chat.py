"""
Endpoint /chat : exécute le graphe Corrective RAG et streame en SSE :
  - un événement "step" à chaque nœud terminé (retrieve, grade, rewrite_query, web_search,
    generate, critique) avec un message lisible sur ce qui vient de se passer
  - un événement final "done" avec la réponse complète et les sources

Le graphe (LangGraph, appels Groq/Qdrant synchrones) tourne dans un thread séparé ;
les événements sont poussés sur une queue et relayés au client au fur et à mesure.
"""

import json
import queue
import threading

from fastapi import APIRouter
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.graph.build import app_graph

router = APIRouter()

# Messages lisibles associés à chaque nœud, une fois qu'il a terminé.
_STEP_LABELS = {
    "retrieve": "Recherche dans la base de connaissances...",
    "grade": "Évaluation de la pertinence des documents...",
    "rewrite_query": "Documents insuffisants, reformulation de la question...",
    "web_search": "Recherche web complémentaire...",
    "generate": "Génération de la réponse...",
    "critique": "Vérification que la réponse est bien fondée...",
}


class ChatRequest(BaseModel):
    question: str


def _run_graph_in_thread(question: str, event_queue: "queue.Queue"):
    """Exécute le graphe (bloquant) dans un thread, pousse chaque étape sur la queue."""
    initial_state = {
        "question": question,
        "search_query": "",
        "documents": [],
        "generation": "",
        "retries": 0,
        "max_retries": 2,
        "grounded": False,
    }
    full_state = dict(initial_state)

    try:
        for step in app_graph.stream(initial_state, stream_mode="updates"):
            for node_name, update in step.items():
                full_state.update(update)
                event_queue.put(
                    {
                        "event": "step",
                        "data": json.dumps(
                            {
                                "node": node_name,
                                "label": _STEP_LABELS.get(node_name, node_name),
                            }
                        ),
                    }
                )

        event_queue.put(
            {
                "event": "done",
                "data": json.dumps(
                    {
                        "answer": full_state["generation"],
                        "sources": [d["source"] for d in full_state["documents"]],
                        "grounded": full_state["grounded"],
                        "retries": full_state["retries"],
                    }
                ),
            }
        )
    except Exception as exc:  # noqa: BLE001 - on remonte l'erreur au client SSE
        event_queue.put({"event": "error", "data": json.dumps({"message": str(exc)})})
    finally:
        event_queue.put(None)  # signal de fin de flux


@router.post("/chat")
async def chat(req: ChatRequest):
    event_queue: "queue.Queue" = queue.Queue()

    thread = threading.Thread(
        target=_run_graph_in_thread, args=(req.question, event_queue), daemon=True
    )
    thread.start()

    async def event_generator():
        loop_queue = event_queue
        while True:
            item = await _get_from_queue(loop_queue)
            if item is None:
                break
            yield item

    return EventSourceResponse(event_generator())


async def _get_from_queue(q: "queue.Queue"):
    """Attend un item de la queue sans bloquer l'event loop asyncio."""
    import anyio

    return await anyio.to_thread.run_sync(q.get)
from typing import List, TypedDict


class Document(TypedDict):
    content: str
    source: str


class GraphState(TypedDict):
    """État partagé, transmis et modifié par chaque nœud du graphe."""

    question: str  # question originale de l'utilisateur
    search_query: str  # question éventuellement reformulée (utilisée pour retrieve)
    documents: List[Document]  # documents jugés pertinents à date
    generation: str  # réponse générée
    retries: int  # nombre de boucles de correction déjà effectuées
    max_retries: int  # borne (évite une boucle infinie)
    grounded: bool  # la réponse est-elle bien fondée sur les documents (jugé par critique) ?

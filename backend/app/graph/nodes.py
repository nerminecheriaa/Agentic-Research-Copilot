from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient

from app.config import settings
from app.graph.llm import llm
from app.graph.retriever import similarity_search
from app.graph.state import GraphState

# ---------------------------------------------------------------------------
# retrieve : recherche par similarité dans Qdrant
# ---------------------------------------------------------------------------


def retrieve_node(state: GraphState) -> dict:
    query = state.get("search_query") or state["question"]
    new_docs = similarity_search(query, k=3)
    print(f"[retrieve] {len(new_docs)} documents récupérés pour : {query!r}")

    # Fusionne avec les documents déjà présents (ex : ajoutés par web_search juste avant),
    # au lieu de les écraser, en évitant les doublons par contenu.
    existing = state.get("documents", [])
    seen = {d["content"] for d in existing}
    merged = existing + [d for d in new_docs if d["content"] not in seen]
    return {"documents": merged}


# ---------------------------------------------------------------------------
# grade : un LLM juge, document par document, s'il répond à la question
# ---------------------------------------------------------------------------


class DocumentGrade(BaseModel):
    relevant: bool = Field(description="True si le document aide à répondre à la question")


_grade_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Contexte du domaine : ici 'RAG' signifie Retrieval-Augmented Generation, "
            "une technique d'IA/NLP qui combine recherche documentaire et génération de texte par LLM. "
            "Ce n'est PAS l'acronyme de gestion de projet Rouge/Ambre/Vert (Red/Amber/Green).\n\n"
            "Tu évalues si un extrait de document est pertinent pour répondre à une question. "
            "Sois strict : réponds True seulement si l'extrait contient une information "
            "qui aide réellement à répondre.\n"
            "Réponds STRICTEMENT sous forme d'objet JSON avec la clé 'relevant' (valeur true ou false).",
        ),
        ("human", "Question : {question}\n\nExtrait :\n{document}"),
    ]
)
_grader = (_grade_prompt | llm.with_structured_output(DocumentGrade, method="json_mode")).with_retry(
    stop_after_attempt=4, wait_exponential_jitter=True
)


def grade_documents_node(state: GraphState) -> dict:
    relevant_docs = []
    for doc in state["documents"]:
        grade = _grader.invoke({"question": state["question"], "document": doc["content"]})
        print(f"  [debug] source={doc['source']!r} relevant={grade.relevant} "
              f"extrait={doc['content'][:120]!r}")
        if grade.relevant:
            relevant_docs.append(doc)

    print(f"[grade] {len(relevant_docs)}/{len(state['documents'])} documents jugés pertinents")
    return {"documents": relevant_docs}


def decide_after_grade(state: GraphState) -> str:
    """Route : assez de documents pertinents -> generate, sinon -> rewrite_query."""
    if len(state["documents"]) >= 2 or state["retries"] >= state["max_retries"]:
        return "generate"
    return "rewrite_query"


# ---------------------------------------------------------------------------
# rewrite_query : reformule la question pour améliorer la recherche suivante
# ---------------------------------------------------------------------------

_rewrite_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Contexte du domaine : ici 'RAG' signifie Retrieval-Augmented Generation, "
            "une technique d'IA/NLP qui combine recherche documentaire et génération de texte par LLM. "
            "Ce n'est PAS l'acronyme de gestion de projet Rouge/Ambre/Vert (Red/Amber/Green).\n\n"
            "Tu reformules une question pour améliorer une recherche documentaire dans un corpus "
            "de papers de recherche en IA/NLP. Garde le même sens, rends-la plus précise et riche "
            "en mots-clés techniques. Si une reformulation précédente est fournie et n'a pas suffi, "
            "propose un angle VRAIMENT différent (autres mots-clés, autre facette de la question) "
            "plutôt que de répéter la même formulation. "
            "Réponds uniquement avec la question reformulée, rien d'autre.",
        ),
        (
            "human",
            "Question originale : {question}\n"
            "Reformulation précédente (si tentative précédente insuffisante) : {previous_attempt}",
        ),
    ]
)
_rewriter = (_rewrite_prompt | llm).with_retry(stop_after_attempt=4, wait_exponential_jitter=True)


def rewrite_query_node(state: GraphState) -> dict:
    previous = state.get("search_query") or "(aucune, première tentative)"
    new_query = _rewriter.invoke(
        {"question": state["question"], "previous_attempt": previous}
    ).content.strip()
    print(f"[rewrite_query] {state['question']!r} -> {new_query!r}")
    return {"search_query": new_query, "retries": state["retries"] + 1}


# ---------------------------------------------------------------------------
# web_search : filet de sécurité quand Qdrant ne suffit pas (Tavily)
# ---------------------------------------------------------------------------

_tavily = TavilyClient(api_key=settings.tavily_api_key) if settings.tavily_api_key else None


def web_search_node(state: GraphState) -> dict:
    if _tavily is None:
        print("[web_search] TAVILY_API_KEY absente, étape ignorée")
        return {}

    query = state.get("search_query") or state["question"]
    results = _tavily.search(query=query, max_results=3)
    web_docs = [
        {"content": r["content"], "source": r["url"]} for r in results.get("results", [])
    ]
    print(f"[web_search] {len(web_docs)} résultats web ajoutés")
    return {"documents": state["documents"] + web_docs}


# ---------------------------------------------------------------------------
# generate : génère la réponse à partir des documents retenus
# ---------------------------------------------------------------------------

_generate_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Tu réponds à des questions techniques en te basant STRICTEMENT sur le contexte fourni. "
            "Si le contexte ne suffit pas, dis-le clairement au lieu d'inventer.",
        ),
        ("human", "Contexte :\n{context}\n\nQuestion : {question}"),
    ]
)
_generator = (_generate_prompt | llm).with_retry(stop_after_attempt=4, wait_exponential_jitter=True)


def generate_node(state: GraphState) -> dict:
    context = "\n\n---\n\n".join(d["content"] for d in state["documents"])
    answer = _generator.invoke({"context": context, "question": state["question"]}).content
    print("[generate] réponse générée")
    return {"generation": answer}


# ---------------------------------------------------------------------------
# critique : un second agent vérifie que la réponse est fondée sur le contexte
# ---------------------------------------------------------------------------


class Critique(BaseModel):
    grounded: bool = Field(description="True si la réponse est bien fondée sur le contexte, sans invention")


_critique_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Tu vérifies si une réponse est entièrement fondée sur le contexte fourni, "
            "sans affirmation inventée ou non supportée.\n"
            "Réponds STRICTEMENT sous forme d'objet JSON avec la clé 'grounded' (valeur true ou false).",
        ),
        ("human", "Contexte :\n{context}\n\nRéponse à vérifier :\n{generation}"),
    ]
)
_critic = (_critique_prompt | llm.with_structured_output(Critique, method="json_mode")).with_retry(
    stop_after_attempt=4, wait_exponential_jitter=True
)


def critique_node(state: GraphState) -> dict:
    context = "\n\n---\n\n".join(d["content"] for d in state["documents"])
    result = _critic.invoke({"context": context, "generation": state["generation"]})
    print(f"[critique] fondée sur le contexte : {result.grounded}")
    return {"grounded": result.grounded}


def decide_after_critique(state: GraphState) -> str:
    """Route : réponse validée -> fin, sinon retry (borné) en reformulant la question."""
    if result_is_final(state):
        return "end"
    return "rewrite_query"


def result_is_final(state: GraphState) -> bool:
    return state["grounded"] or state["retries"] >= state["max_retries"]

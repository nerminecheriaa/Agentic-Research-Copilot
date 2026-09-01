"""
Tests sur la logique de décision du graphe (decide_after_grade, decide_after_critique)
et sur la fusion des documents dans retrieve_node. Ces fonctions sont pures ou mockées :
aucun appel réseau réel vers Groq/Qdrant/Tavily n'est fait.
"""

from unittest.mock import patch

from app.graph.nodes import (
    decide_after_critique,
    decide_after_grade,
    result_is_final,
    retrieve_node,
)


def _base_state(**overrides):
    state = {
        "question": "What is corrective RAG?",
        "search_query": "",
        "documents": [],
        "generation": "",
        "retries": 0,
        "max_retries": 2,
        "grounded": False,
    }
    state.update(overrides)
    return state


def test_decide_after_grade_enough_documents_goes_to_generate():
    state = _base_state(
        documents=[{"content": "a", "source": "x"}, {"content": "b", "source": "y"}]
    )
    assert decide_after_grade(state) == "generate"


def test_decide_after_grade_insufficient_documents_triggers_rewrite():
    state = _base_state(documents=[{"content": "a", "source": "x"}], retries=0)
    assert decide_after_grade(state) == "rewrite_query"


def test_decide_after_grade_stops_retrying_once_max_reached():
    state = _base_state(documents=[], retries=2, max_retries=2)
    assert decide_after_grade(state) == "generate"


def test_decide_after_critique_grounded_ends():
    state = _base_state(grounded=True, retries=0)
    assert decide_after_critique(state) == "end"


def test_decide_after_critique_not_grounded_retries_if_budget_left():
    state = _base_state(grounded=False, retries=0, max_retries=2)
    assert decide_after_critique(state) == "rewrite_query"


def test_decide_after_critique_stops_once_retries_exhausted():
    state = _base_state(grounded=False, retries=2, max_retries=2)
    assert decide_after_critique(state) == "end"


def test_result_is_final():
    assert result_is_final(_base_state(grounded=True, retries=0, max_retries=2)) is True
    assert result_is_final(_base_state(grounded=False, retries=2, max_retries=2)) is True
    assert result_is_final(_base_state(grounded=False, retries=0, max_retries=2)) is False


def test_retrieve_node_merges_with_existing_documents_without_duplicates():
    """Régression : retrieve_node écrasait autrefois les documents ajoutés par
    web_search au lieu de les fusionner (bug corrigé en Semaine 1)."""
    existing = [{"content": "already here", "source": "web"}]
    new_from_qdrant = [
        {"content": "already here", "source": "web-dup"},  # doublon, doit être ignoré
        {"content": "new chunk", "source": "paper.pdf"},
    ]
    state = {"question": "q", "search_query": "q", "documents": existing}

    with patch("app.graph.nodes.similarity_search", return_value=new_from_qdrant):
        result = retrieve_node(state)

    contents = [d["content"] for d in result["documents"]]
    assert contents == ["already here", "new chunk"]

from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    critique_node,
    decide_after_critique,
    decide_after_grade,
    generate_node,
    grade_documents_node,
    retrieve_node,
    rewrite_query_node,
    web_search_node,
)
from app.graph.state import GraphState


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade", grade_documents_node)
    graph.add_node("rewrite_query", rewrite_query_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("generate", generate_node)
    graph.add_node("critique", critique_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "grade")

    graph.add_conditional_edges(
        "grade",
        decide_after_grade,
        {"generate": "generate", "rewrite_query": "rewrite_query"},
    )

    graph.add_edge("rewrite_query", "web_search")
    graph.add_edge("web_search", "retrieve")

    graph.add_edge("generate", "critique")

    graph.add_conditional_edges(
        "critique",
        decide_after_critique,
        {"end": END, "rewrite_query": "rewrite_query"},
    )

    return graph.compile()


app_graph = build_graph()

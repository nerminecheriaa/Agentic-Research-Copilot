"""
Teste le graphe Corrective RAG en ligne de commande.

Usage :
    python -m app.graph.run "Qu'est-ce que le corrective RAG ?"
"""

import sys

from app.graph.build import app_graph


def run(question: str):
    initial_state = {
        "question": question,
        "search_query": "",
        "documents": [],
        "generation": "",
        "retries": 0,
        "max_retries": 2,
        "grounded": False,
    }

    final_state = app_graph.invoke(initial_state)

    print("\n" + "=" * 60)
    print("RÉPONSE :")
    print(final_state["generation"])
    print("=" * 60)
    print(f"Sources : {[d['source'] for d in final_state['documents']]}")
    print(f"Retries utilisés : {final_state['retries']}/{final_state['max_retries']}")


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Qu'est-ce que le corrective RAG ?"
    run(question)

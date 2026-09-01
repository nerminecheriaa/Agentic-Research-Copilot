"""
Teste /chat directement via requests, sans navigateur (élimine CORS, origine
file://, etc. comme variables possibles).

Usage :
    python -m scripts.test_chat_simple "What is corrective RAG?"
"""

import sys

import requests

URL = "http://localhost:8000/chat"


def main():
    question = " ".join(sys.argv[1:]) or "What is corrective RAG?"
    print(f"Envoi de la requête : {question}")
    print("(patience, ça peut prendre 30s à 2 min selon les retries)\n")

    resp = requests.post(URL, json={"question": question}, timeout=300)
    resp.raise_for_status()
    data = resp.json()

    print("=== RÉPONSE ===")
    print(data["answer"])
    print(f"\nSources : {data['sources']}")
    print(f"Fondée sur le contexte : {data['grounded']}")
    print(f"Retries : {data['retries']}")


if __name__ == "__main__":
    main()

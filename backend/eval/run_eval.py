"""
Évalue le graphe Corrective RAG sur un jeu de questions avec RAGAS.

Usage :
    python -m eval.run_eval
"""

import json
import pathlib
import time

from ragas import EvaluationDataset, evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import AnswerRelevancy, Faithfulness

from app.graph.build import app_graph
from app.graph.llm import llm
from eval.embeddings import FastEmbedEmbeddings

DATASET_PATH = pathlib.Path(__file__).parent / "dataset.json"
RESULTS_PATH = pathlib.Path(__file__).parent / "results.csv"


def run_graph(question: str) -> tuple[str, list[str]]:
    state = {
        "question": question,
        "search_query": "",
        "documents": [],
        "generation": "",
        "retries": 0,
        "max_retries": 2,
        "grounded": False,
    }
    result = app_graph.invoke(state)
    return result["generation"], [d["content"] for d in result["documents"]]


def main():
    questions = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    samples = []
    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {q['question']}")
        answer, contexts = run_graph(q["question"])
        samples.append(
            {
                "user_input": q["question"],
                "response": answer,
                "retrieved_contexts": contexts or ["(aucun contexte retenu)"],
            }
        )
        time.sleep(2)  # ménage le rate limit Groq (palier gratuit) entre questions

    dataset = EvaluationDataset.from_list(samples)

    print("\nCalcul des métriques RAGAS (faithfulness, answer_relevancy)...")
    result = evaluate(
        dataset=dataset,
        metrics=[Faithfulness(), AnswerRelevancy()],
        llm=LangchainLLMWrapper(llm),
        embeddings=LangchainEmbeddingsWrapper(FastEmbedEmbeddings()),
    )

    print("\n=== Résultats RAGAS ===")
    print(result)

    result.to_pandas().to_csv(RESULTS_PATH, index=False)
    print(f"\nDétail par question sauvegardé dans {RESULTS_PATH}")


if __name__ == "__main__":
    main()

"""
Télécharge un corpus de papers arXiv en local.

Usage :
    python -m app.ingestion.fetch_arxiv --query "retrieval augmented generation" --max-results 20
"""

import argparse
import pathlib

import arxiv

RAW_DIR = pathlib.Path(__file__).resolve().parents[2] / "data" / "raw"


def fetch(query: str, max_results: int = 20) -> list[pathlib.Path]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    saved = []
    for result in client.results(search):
        arxiv_id = result.get_short_id()
        target = RAW_DIR / f"{arxiv_id}.pdf"
        if target.exists():
            saved.append(target)
            continue
        print(f"Téléchargement : {result.title[:80]}...")
        result.download_pdf(dirpath=str(RAW_DIR), filename=target.name)
        saved.append(target)

    print(f"{len(saved)} papers disponibles dans {RAW_DIR}")
    return saved


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Requête de recherche arXiv")
    parser.add_argument("--max-results", type=int, default=20)
    args = parser.parse_args()
    fetch(args.query, args.max_results)

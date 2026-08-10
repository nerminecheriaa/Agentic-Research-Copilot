"""
Construit l'index Qdrant à partir des PDF téléchargés dans data/raw/.

Utilise FastEmbed (modèle local BAAI/bge-small-en-v1.5, pas de clé API requise)
via l'intégration native du qdrant-client.

Usage :
    python -m app.ingestion.build_index
"""

import pathlib
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from qdrant_client import QdrantClient

from app.config import settings

RAW_DIR = pathlib.Path(__file__).resolve().parents[2] / "data" / "raw"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"


def extract_text(pdf_path: pathlib.Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def build_index():
    pdfs = sorted(RAW_DIR.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(
            f"Aucun PDF trouvé dans {RAW_DIR}. "
            "Lance d'abord : python -m app.ingestion.fetch_arxiv --query '...'"
        )

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)

    documents, metadatas, ids = [], [], []
    for pdf_path in pdfs:
        text = extract_text(pdf_path)
        if not text.strip():
            print(f"  ! texte vide, ignoré : {pdf_path.name}")
            continue
        chunks = splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({"source": pdf_path.name, "chunk_index": i})
            ids.append(str(uuid.uuid4()))
        print(f"  {pdf_path.name} -> {len(chunks)} chunks")

    client = QdrantClient(url=settings.qdrant_url)
    client.set_model(EMBED_MODEL)

    client.add(
        collection_name=settings.qdrant_collection,
        documents=documents,
        metadata=metadatas,
        ids=ids,
    )

    print(
        f"\n{len(documents)} chunks indexés dans la collection "
        f"'{settings.qdrant_collection}' ({settings.qdrant_url})"
    )


if __name__ == "__main__":
    build_index()

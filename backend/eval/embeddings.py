from fastembed import TextEmbedding
from langchain_core.embeddings import Embeddings


class FastEmbedEmbeddings(Embeddings):
    """Wrapper minimal pour réutiliser le même modèle d'embedding local (FastEmbed)
    que celui utilisé pour l'indexation, ici pour les métriques RAGAS qui en ont besoin
    (answer_relevancy)."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self._model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vec.tolist() for vec in self._model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return next(self._model.embed([text])).tolist()

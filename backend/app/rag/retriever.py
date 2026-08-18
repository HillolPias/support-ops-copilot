import chromadb
from chromadb.utils import embedding_functions
from app.config import CHROMA_PERSIST_DIR
from app.models import RetrievedChunk
from app.rag.ingest import COLLECTION_NAME

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        _collection = _client.get_collection(
            name=COLLECTION_NAME, embedding_function=embed_fn
        )
    return _collection


def retrieve(query: str, k: int = 4) -> list[RetrievedChunk]:
    collection = _get_collection()
    results = collection.query(query_texts=[query], n_results=k)

    chunks = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for text, meta, dist in zip(docs, metas, dists):
        similarity = max(0.0, 1.0 - dist)
        chunks.append(
            RetrievedChunk(
                source=meta.get("source", "unknown"),
                text=text,
                score=round(similarity, 3),
            )
        )
    return chunks

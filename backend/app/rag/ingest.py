import os
import glob
import chromadb
from chromadb.utils import embedding_functions
from app.config import CHROMA_PERSIST_DIR, DOCS_DIR

COLLECTION_NAME = "support_kb"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def chunk_text(
    text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]


def ingest() -> None:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME, embedding_function=embed_fn
    )

    doc_paths = sorted(glob.glob(os.path.join(DOCS_DIR, "*.md")))
    ids, texts, metadatas = [], [], []
    for path in doc_paths:
        source = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        for i, chunk in enumerate(chunk_text(content)):
            ids.append(f"{source}::{i}")
            texts.append(chunk)
            metadatas.append({"source": source})

    collection.add(ids=ids, documents=texts, metadatas=metadatas)
    print(f"Ingested {len(ids)} chunks from {len(doc_paths)} documents.")


if __name__ == "__main__":
    ingest()

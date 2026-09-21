import json
import math
from pathlib import Path


STORE_FILE = Path("vector_store.json")


def load_store():
    if not STORE_FILE.exists():
        return []

    try:
        with open(
            STORE_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception:
        return []


def save_store(data):
    with open(
        STORE_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False
        )


def cosine_similarity(vector_a, vector_b):
    if not vector_a or not vector_b:
        return 0.0

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b
        )
    )

    magnitude_a = math.sqrt(
        sum(
            value * value
            for value in vector_a
        )
    )

    magnitude_b = math.sqrt(
        sum(
            value * value
            for value in vector_b
        )
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def store_chunks(
    chunks,
    embeddings,
    document_name
):
    """
    Store chunks and their lightweight embeddings.
    """

    store = load_store()

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        store.append(
            {
                "document_name": document_name,
                "chunk_index": index,
                "text": chunk,
                "embedding": embedding
            }
        )

    save_store(store)

    return len(chunks)


def search_chunks(
    query_embedding,
    top_k=5
):
    """
    Search stored chunks using cosine similarity.
    """

    store = load_store()

    if not store:
        return []

    results = []

    for item in store:

        similarity = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        results.append(
            {
                "text": item["text"],
                "document_name": item["document_name"],
                "chunk_index": item["chunk_index"],
                "score": similarity
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]
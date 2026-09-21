from sentence_transformers import SentenceTransformer


# Embedding model load
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks: list[str]):
    """
    Convert text chunks into vector embeddings.
    """

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True
    )

    return embeddings
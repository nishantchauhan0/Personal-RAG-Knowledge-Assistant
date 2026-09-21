from sentence_transformers import SentenceTransformer


# Model will be loaded only when needed.
model = None


def get_model():
    global model

    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")

    return model


def create_embeddings(chunks: list[str]):
    """
    Convert text chunks into vector embeddings.
    """

    embedding_model = get_model()

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True
    )

    return embeddings
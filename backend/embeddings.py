import hashlib
import math
import re


EMBEDDING_DIMENSION = 256


def tokenize(text: str):
    return re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())


def create_single_embedding(text: str):
    """
    Create a lightweight deterministic text embedding.

    This does not require a machine-learning model,
    so it uses very little RAM and is suitable for
    low-memory deployment environments.
    """

    vector = [0.0] * EMBEDDING_DIMENSION

    tokens = tokenize(text)

    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.md5(
            token.encode("utf-8")
        ).digest()

        index = int.from_bytes(
            digest[:4],
            byteorder="big"
        ) % EMBEDDING_DIMENSION

        sign = 1.0 if digest[4] % 2 == 0 else -1.0

        vector[index] += sign

    magnitude = math.sqrt(
        sum(value * value for value in vector)
    )

    if magnitude > 0:
        vector = [
            value / magnitude
            for value in vector
        ]

    return vector


def create_embeddings(chunks: list[str]):
    """
    Create lightweight embeddings for multiple chunks.
    """

    return [
        create_single_embedding(chunk)
        for chunk in chunks
    ]
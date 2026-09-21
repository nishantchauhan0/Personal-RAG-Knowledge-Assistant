import re

from backend.embeddings import create_embeddings
from backend.vector_store import search_chunks


def normalize_text(text: str):
    """
    Convert text into normalized lowercase words.
    """

    return set(
        re.findall(
            r"\b[a-zA-Z0-9+#.-]+\b",
            text.lower()
        )
    )


def calculate_keyword_score(
    question: str,
    text: str
):
    """
    Calculate keyword overlap between the question
    and document chunk.
    """

    question_words = normalize_text(question)
    text_words = normalize_text(text)

    if not question_words or not text_words:
        return 0.0

    common_words = question_words.intersection(
        text_words
    )

    return len(common_words) / len(
        question_words
    )


def retrieve_relevant_chunks(
    question: str,
    top_k: int = 5
):
    """
    Retrieve relevant chunks using a combination
    of lightweight vector similarity and keyword
    matching.

    Keyword matching helps when the user asks about
    exact technology names or specific terms.
    """

    question_embedding = create_embeddings(
        [question]
    )[0]

    vector_results = search_chunks(
        question_embedding,
        top_k=10
    )

    if not vector_results:
        return []

    scored_results = []

    for result in vector_results:

        vector_score = result.get(
            "score",
            0.0
        )

        keyword_score = calculate_keyword_score(
            question,
            result["text"]
        )

        # Give more importance to exact keywords
        # while still using vector similarity.
        final_score = (
            (vector_score * 0.4)
            +
            (keyword_score * 0.6)
        )

        scored_results.append(
            {
                "text": result["text"],
                "document_name": result[
                    "document_name"
                ],
                "chunk_index": result[
                    "chunk_index"
                ],
                "score": round(
                    final_score,
                    4
                )
            }
        )

    scored_results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return scored_results[:top_k]
import re
import numpy as np

from backend.embeddings import create_embeddings
from backend.vector_store import collection


STOP_WORDS = {
    "what", "are", "the", "is", "of", "this", "project", "for",
    "and", "in", "to", "a", "an", "on", "with", "how", "does",
    "do", "can", "could", "would", "should", "tell", "me", "about",
    "please", "give", "list", "used", "use", "uses", "main",
    "purpose", "explain", "describe", "which", "where", "why",
    "from", "that", "these", "those"
}


TOPIC_KEYWORDS = {

    "technology": [
        "technology",
        "technologies",
        "tech",
        "software",
        "python",
        "fastapi",
        "react",
        "react.js",
        "javascript",
        "html",
        "css",
        "chromadb",
        "pymupdf",
        "embedding",
        "embeddings",
        "model",
        "language model",
        "large language model",
        "llm",
        "git",
        "github",
        "visual studio code",
        "vscode",
        "frontend",
        "backend",
        "api",
        "framework"
    ],

    "objective": [
        "objective",
        "objectives",
        "goal",
        "purpose",
        "aim"
    ],

    "functional": [
        "functional",
        "requirement",
        "requirements",
        "feature",
        "features",
        "upload",
        "question",
        "answer"
    ],

    "tools": [
        "tools",
        "tool",
        "hardware",
        "software requirements"
    ],

    "rag": [
        "rag",
        "retrieval",
        "retrieval-augmented",
        "generation",
        "knowledge assistant"
    ],

    "embedding": [
        "embedding",
        "embeddings",
        "vector",
        "vectors",
        "semantic",
        "similarity"
    ],

    "database": [
        "database",
        "db",
        "chromadb",
        "chroma",
        "vector database",
        "storage",
        "collection"
    ],

    "architecture": [
        "architecture",
        "workflow",
        "pipeline",
        "data flow",
        "dfd",
        "system architecture"
    ]
}


SECTION_RULES = {

    "technology": [
        "4.2 SOFTWARE REQUIREMENTS",
        "4.2 SOFTWARE",
        "SOFTWARE / TECHNOLOGY",
        "SOFTWARE REQUIREMENTS",
        "TECHNOLOGIES USED",
        "TECHNOLOGY USED",
        "TECHNOLOGY STACK",
        "TECH STACK"
    ],

    "objective": [
        "2. OBJECTIVES",
        "2. OBJECTIVE",
        "OBJECTIVES"
    ],

    "functional": [
        "4.3 FUNCTIONAL REQUIREMENTS",
        "FUNCTIONAL REQUIREMENTS"
    ],

    "tools": [
        "4. TOOLS / HARDWARE / SOFTWARE REQUIRED",
        "TOOLS / HARDWARE / SOFTWARE REQUIRED"
    ],

    "rag": [
        "RETRIEVAL-AUGMENTED GENERATION",
        "RETRIEVAL AUGMENTED GENERATION",
        "PROPOSED SYSTEM",
        "RAG APPLICATION",
        "KNOWLEDGE ASSISTANT"
    ],

    "embedding": [
        "EMBEDDING",
        "EMBEDDINGS",
        "VECTOR"
    ],

    "database": [
        "DATABASE DESIGN",
        "VECTOR DATABASE",
        "CHROMADB"
    ],

    "architecture": [
        "5.1 SYSTEM ARCHITECTURE",
        "SYSTEM ARCHITECTURE",
        "DATA FLOW",
        "CONTEXT DATA FLOW"
    ]
}


def extract_keywords(text: str):
    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )

    return list(
        dict.fromkeys(
            word
            for word in words
            if word not in STOP_WORDS
            and len(word) > 2
        )
    )


def detect_question_topics(question: str):
    q = question.lower()

    topics = []

    if any(
        phrase in q
        for phrase in [
            "technology",
            "technologies",
            "tech",
            "tech stack",
            "technology stack",
            "software used",
            "software technologies",
            "programming language",
            "framework",
            "frontend",
            "backend"
        ]
    ):
        topics.append("technology")

    if any(
        phrase in q
        for phrase in [
            "objective",
            "objectives",
            "goal",
            "aim",
            "purpose"
        ]
    ):
        topics.append("objective")

    if any(
        phrase in q
        for phrase in [
            "functional requirement",
            "functional requirements",
            "features",
            "functionality"
        ]
    ):
        topics.append("functional")

    if any(
        phrase in q
        for phrase in [
            "tool",
            "tools",
            "hardware"
        ]
    ):
        topics.append("tools")

    if (
        "rag" in q
        or "retrieval augmented" in q
        or "retrieval-augmented" in q
    ):
        topics.append("rag")

    if any(
        phrase in q
        for phrase in [
            "embedding",
            "embeddings",
            "vector",
            "semantic similarity"
        ]
    ):
        topics.append("embedding")

    if any(
        phrase in q
        for phrase in [
            "database",
            "vector database",
            "chromadb"
        ]
    ):
        topics.append("database")

    if any(
        phrase in q
        for phrase in [
            "architecture",
            "workflow",
            "pipeline",
            "data flow",
            "dfd"
        ]
    ):
        topics.append("architecture")

    return list(
        dict.fromkeys(topics)
    )


def calculate_keyword_score(
    question: str,
    document: str
):
    keywords = extract_keywords(question)

    if not keywords:
        return 0.0

    document_lower = document.lower()

    matches = 0

    for keyword in keywords:

        if keyword in document_lower:
            matches += 1

    return matches / len(keywords)


def calculate_topic_score(
    question: str,
    document: str
):
    topics = detect_question_topics(question)

    if not topics:
        return 0.0

    document_lower = document.lower()

    topic_scores = []

    for topic in topics:

        keywords = TOPIC_KEYWORDS.get(
            topic,
            []
        )

        if not keywords:
            continue

        matches = 0

        for keyword in keywords:

            if keyword.lower() in document_lower:
                matches += 1

        score = min(
            matches / 5.0,
            1.0
        )

        topic_scores.append(
            score
        )

    if not topic_scores:
        return 0.0

    return sum(topic_scores) / len(topic_scores)


def calculate_section_score(
    question: str,
    document: str
):
    topics = detect_question_topics(question)

    if not topics:
        return 0.0

    document_upper = document.upper()

    matched = 0

    for topic in topics:

        section_names = SECTION_RULES.get(
            topic,
            []
        )

        for section_name in section_names:

            if section_name.upper() in document_upper:

                matched += 1
                break

    return min(
        matched / len(topics),
        1.0
    )


def calculate_technology_content_score(
    question: str,
    document: str
):
    """
    Gives additional priority to chunks that contain
    actual software/technology information.
    """

    q = question.lower()

    technology_question = any(
        phrase in q
        for phrase in [
            "technology",
            "technologies",
            "tech stack",
            "technology stack",
            "software used",
            "software technologies",
            "programming language",
            "framework"
        ]
    )

    if not technology_question:
        return 0.0

    document_lower = document.lower()

    technology_terms = [
        "python",
        "fastapi",
        "flask",
        "react",
        "react.js",
        "javascript",
        "html",
        "css",
        "chromadb",
        "pymupdf",
        "embedding model",
        "embedding api",
        "embeddings",
        "large language model",
        "language model",
        "llm",
        "git",
        "github",
        "visual studio code",
        "vscode",
        "frontend",
        "backend",
        "api",
        "framework",
        "vector database"
    ]

    matches = sum(
        1
        for term in technology_terms
        if term in document_lower
    )

    if matches >= 6:
        return 1.0

    if matches >= 4:
        return 0.9

    if matches >= 3:
        return 0.8

    if matches >= 2:
        return 0.6

    if matches == 1:
        return 0.3

    return 0.0


def calculate_software_section_score(
    question: str,
    document: str
):
    """
    Strong bonus for the actual Software Requirements
    section of the synopsis.
    """

    q = question.lower()

    technology_question = any(
        phrase in q
        for phrase in [
            "technology",
            "technologies",
            "tech stack",
            "technology stack",
            "software used",
            "software technologies",
            "programming language",
            "framework"
        ]
    )

    if not technology_question:
        return 0.0

    document_upper = document.upper()

    strong_section_phrases = [
        "4.2 SOFTWARE REQUIREMENTS",
        "SOFTWARE / TECHNOLOGY",
        "TECHNOLOGIES USED",
        "TECHNOLOGY STACK",
        "TECH STACK"
    ]

    for phrase in strong_section_phrases:

        if phrase in document_upper:
            return 1.0

    # Chunk may start in the middle of the section,
    # so also recognize its characteristic content.
    software_indicators = [
        "BACKEND/API:",
        "DOCUMENT PROCESSING:",
        "EMBEDDING MODEL/API:",
        "VECTOR DATABASE:",
        "LANGUAGE MODEL:",
        "DEVELOPMENT TOOLS:",
        "BROWSER:"
    ]

    matches = sum(
        1
        for indicator in software_indicators
        if indicator in document_upper
    )

    if matches >= 3:
        return 0.9

    if matches >= 2:
        return 0.7

    if matches == 1:
        return 0.4

    return 0.0


def calculate_hardware_penalty(
    question: str,
    document: str
):
    """
    Detect hardware-only content.

    Hardware content should not be selected for
    software technology questions.
    """

    q = question.lower()
    document_lower = document.lower()

    technology_question = any(
        phrase in q
        for phrase in [
            "technology",
            "technologies",
            "tech stack",
            "technology stack",
            "software used",
            "software technologies",
            "programming language",
            "framework"
        ]
    )

    if not technology_question:
        return 0.0

    hardware_terms = [
        "processor",
        "ram",
        "storage",
        "display",
        "internet connection",
        "intel core",
        "laptop",
        "personal computer",
        "hardware requirements"
    ]

    matches = sum(
        1
        for term in hardware_terms
        if term in document_lower
    )

    if matches >= 5:
        return 1.0

    if matches >= 3:
        return 0.8

    if matches >= 2:
        return 0.5

    if matches == 1:
        return 0.2

    return 0.0


def is_hardware_only_chunk(
    question: str,
    document: str
):
    """
    For technology questions, identify chunks that are
    primarily hardware requirements.

    This prevents Chunk 8 type content from appearing
    in the final technology retrieval results.
    """

    q = question.lower()
    document_lower = document.lower()

    technology_question = any(
        phrase in q
        for phrase in [
            "technology",
            "technologies",
            "tech stack",
            "technology stack",
            "software used",
            "software technologies",
            "programming language",
            "framework"
        ]
    )

    if not technology_question:
        return False

    hardware_terms = [
        "processor",
        "ram",
        "storage",
        "display",
        "internet connection",
        "intel core",
        "laptop",
        "personal computer",
        "hardware requirements"
    ]

    technology_terms = [
        "python",
        "fastapi",
        "flask",
        "react",
        "javascript",
        "html",
        "css",
        "chromadb",
        "pymupdf",
        "embedding",
        "vector database",
        "language model",
        "llm",
        "git",
        "github",
        "visual studio code",
        "frontend",
        "backend",
        "api"
    ]

    hardware_matches = sum(
        1
        for term in hardware_terms
        if term in document_lower
    )

    technology_matches = sum(
        1
        for term in technology_terms
        if term in document_lower
    )

    if hardware_matches >= 3 and technology_matches <= 1:
        return True

    if "hardware requirements" in document_lower:
        if technology_matches <= 2:
            return True

    return False


def calculate_exact_phrase_score(
    question: str,
    document: str
):
    question_lower = question.lower()
    document_lower = document.lower()

    # TECHNOLOGY
    if any(
        phrase in question_lower
        for phrase in [
            "technology",
            "technologies",
            "tech stack",
            "technology stack",
            "software used",
            "software technologies",
            "programming language",
            "framework"
        ]
    ):

        technology_phrases = [
            "4.2 software requirements",
            "4.2 software",
            "software / technology",
            "software requirements",
            "technologies used",
            "technology used",
            "technology stack",
            "tech stack"
        ]

        for phrase in technology_phrases:

            if phrase in document_lower:
                return 1.0

    # FUNCTIONAL REQUIREMENTS
    if (
        "functional requirement" in question_lower
        or "functional requirements" in question_lower
    ):

        if "functional requirements" in document_lower:
            return 1.0

    # OBJECTIVE
    if (
        "main objective" in question_lower
        or "objectives" in question_lower
        or "objective" in question_lower
    ):

        if "objectives" in document_lower:
            return 1.0

    # DATABASE
    if "database" in question_lower:

        if (
            "vector database" in document_lower
            or "chromadb" in document_lower
            or "database design" in document_lower
        ):
            return 1.0

    # EMBEDDINGS
    if (
        "embedding" in question_lower
        or "embeddings" in question_lower
    ):

        if (
            "embedding" in document_lower
            or "embeddings" in document_lower
            or "vector" in document_lower
        ):
            return 1.0

    return 0.0


def cosine_similarity(
    vector_a,
    vector_b
):
    vector_a = np.asarray(
        vector_a,
        dtype=float
    )

    vector_b = np.asarray(
        vector_b,
        dtype=float
    )

    denominator = (
        np.linalg.norm(vector_a)
        * np.linalg.norm(vector_b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(
            vector_a,
            vector_b
        )
        / denominator
    )


def retrieve_relevant_chunks(
    question: str,
    top_k: int = 5
):
    stored_data = collection.get(
        include=[
            "documents",
            "metadatas",
            "embeddings"
        ]
    )

    documents = stored_data.get(
        "documents",
        []
    )

    metadatas = stored_data.get(
        "metadatas",
        []
    )

    embeddings = stored_data.get(
        "embeddings",
        []
    )

    if not documents:
        return []

    question_embedding = create_embeddings(
        [question]
    )[0]

    question_topics = detect_question_topics(
        question
    )

    candidates = []

    for i, document in enumerate(documents):

        # --------------------------------
        # Hardware-only filtering
        # --------------------------------

        if is_hardware_only_chunk(
            question,
            document
        ):
            continue

        # --------------------------------
        # Semantic similarity
        # --------------------------------

        if (
            i < len(embeddings)
            and embeddings[i] is not None
        ):

            semantic_score = cosine_similarity(
                question_embedding,
                embeddings[i]
            )

        else:

            semantic_score = 0.0

        # --------------------------------
        # Keyword score
        # --------------------------------

        keyword_score = calculate_keyword_score(
            question,
            document
        )

        # --------------------------------
        # Topic score
        # --------------------------------

        topic_score = calculate_topic_score(
            question,
            document
        )

        # --------------------------------
        # Section score
        # --------------------------------

        section_score = calculate_section_score(
            question,
            document
        )

        # --------------------------------
        # Exact phrase score
        # --------------------------------

        exact_phrase_score = calculate_exact_phrase_score(
            question,
            document
        )

        # --------------------------------
        # Technology content
        # --------------------------------

        technology_content_score = (
            calculate_technology_content_score(
                question,
                document
            )
        )

        # --------------------------------
        # Software section bonus
        # --------------------------------

        software_section_score = (
            calculate_software_section_score(
                question,
                document
            )
        )

        # --------------------------------
        # Hardware penalty
        # --------------------------------

        hardware_penalty = calculate_hardware_penalty(
            question,
            document
        )

        # --------------------------------
        # Final score
        # --------------------------------

        final_score = (

            semantic_score * 0.20

            + keyword_score * 0.10

            + topic_score * 0.10

            + section_score * 0.20

            + exact_phrase_score * 0.10

            + technology_content_score * 0.20

            + software_section_score * 0.20

            - hardware_penalty * 0.20
        )

        metadata = (
            metadatas[i]
            if i < len(metadatas)
            else {}
        )

        candidates.append({

            "text": document,

            "distance": round(
                1 - semantic_score,
                4
            ),

            "score": round(
                final_score,
                4
            ),

            "document_name": metadata.get(
                "document_name",
                "Unknown Document"
            ),

            "chunk_index": metadata.get(
                "chunk_index",
                None
            )
        })

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # --------------------------------
    # Special handling for technology
    # questions
    # --------------------------------

    if "technology" in question_topics:

        technology_candidates = [
            item
            for item in candidates
            if item["score"] > 0
        ]

        if technology_candidates:
            candidates = technology_candidates

    return candidates[:top_k]
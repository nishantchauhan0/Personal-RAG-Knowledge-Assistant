import chromadb
import uuid


# ========================================
# CHROMA DB CLIENT
# ========================================

client = chromadb.PersistentClient(
    path="chroma_db"
)


# ========================================
# COLLECTION
# ========================================

collection = client.get_or_create_collection(
    name="rag_documents"
)


# ========================================
# STORE CHUNKS
# ========================================

def store_chunks(
    chunks,
    embeddings,
    document_name
):
    """
    Store document chunks and embeddings
    in ChromaDB.

    Each chunk gets a unique ID and metadata
    containing the document name and chunk index.
    """

    ids = [
        f"{uuid.uuid4()}_{i}"
        for i in range(len(chunks))
    ]


    metadata = [
        {
            "document_name": document_name,
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]


    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadata
    )


    return len(chunks)


# ========================================
# SEARCH RELEVANT CHUNKS
# ========================================

def search_chunks(
    query_embedding,
    top_k=5
):
    """
    Search relevant chunks from all uploaded
    documents using vector similarity.
    """

    total_documents = collection.count()


    # ========================================
    # EMPTY DATABASE CHECK
    # ========================================

    if total_documents == 0:

        return {
            "documents": [[]],
            "distances": [[]],
            "metadatas": [[]]
        }


    # ========================================
    # LIMIT TOP K
    # ========================================

    top_k = min(
        top_k,
        total_documents
    )


    # ========================================
    # VECTOR SEARCH
    # ========================================

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],

        n_results=top_k,

        include=[
            "documents",
            "distances",
            "metadatas"
        ]
    )


    return results
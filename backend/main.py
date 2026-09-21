from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

from backend.document_loader import extract_text
from backend.chunker import split_text
from backend.embeddings import create_embeddings
from backend.vector_store import store_chunks
from backend.retriever import retrieve_relevant_chunks
from backend.generator import generate_answer


# ========================================
# FASTAPI APP
# ========================================

app = FastAPI(
    title="Personal RAG Knowledge Assistant"
)


# ========================================
# CORS CONFIGURATION
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# UPLOAD FOLDER
# ========================================

UPLOAD_FOLDER = Path("documents")

UPLOAD_FOLDER.mkdir(
    exist_ok=True
)


# ========================================
# QUESTION MODEL
# ========================================

class QuestionRequest(BaseModel):

    question: str


# ========================================
# HOME ROUTE
# ========================================

@app.get("/")
def home():

    return {
        "message": "Personal RAG Knowledge Assistant Backend is running!"
    }


# ========================================
# HEALTH CHECK
# ========================================

@app.get("/health")
def health():

    return {
        "status": "OK"
    }


# ========================================
# UPLOAD DOCUMENT
# ========================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    allowed_extensions = [
        ".pdf",
        ".docx"
    ]


    # ========================================
    # CHECK FILE NAME
    # ========================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="File name is missing."
        )


    # ========================================
    # GET SAFE FILE NAME
    # ========================================

    safe_filename = Path(
        file.filename
    ).name


    file_extension = Path(
        safe_filename
    ).suffix.lower()


    # ========================================
    # CHECK FILE TYPE
    # ========================================

    if file_extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )


    # ========================================
    # SAVE FILE
    # ========================================

    file_path = UPLOAD_FOLDER / safe_filename

    file_content = await file.read()


    with open(
        file_path,
        "wb"
    ) as f:

        f.write(file_content)


    try:

        # ========================================
        # EXTRACT TEXT
        # ========================================

        extracted_text = extract_text(
            str(file_path)
        )


        if not extracted_text.strip():

            raise ValueError(
                "No readable text found in the document."
            )


        # ========================================
        # CREATE CHUNKS
        # ========================================

        chunks = split_text(
            extracted_text
        )


        if not chunks:

            raise ValueError(
                "No chunks could be created from the document."
            )


        # ========================================
        # CREATE EMBEDDINGS
        # ========================================

        embeddings = create_embeddings(
            chunks
        )


        # ========================================
        # STORE IN CHROMADB
        # ========================================

        stored_chunks = store_chunks(
            chunks,
            embeddings,
            safe_filename
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"RAG processing failed: {str(e)}"
        )


    # ========================================
    # SUCCESS RESPONSE
    # ========================================

    return {

        "message":
            f"{safe_filename} processed successfully!",

        "document_name":
            safe_filename,

        "characters_extracted":
            len(extracted_text),

        "chunks_created":
            len(chunks),

        "chunks_stored":
            stored_chunks
    }


# ========================================
# ASK QUESTION
# ========================================

@app.post("/ask")
async def ask_question(
    request: QuestionRequest
):

    question = request.question.strip()


    # ========================================
    # CHECK QUESTION
    # ========================================

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )


    try:

        # ========================================
        # RETRIEVE RELEVANT CHUNKS
        # ========================================

        relevant_chunks = retrieve_relevant_chunks(
            question,
            top_k=5
        )


        # ========================================
        # NO RELEVANT INFORMATION
        # ========================================

        if not relevant_chunks:

            return {

                "question": question,

                "answer":
                    "I could not find relevant information in the uploaded documents.",

                "relevant_chunks": []
            }


        # ========================================
        # EXTRACT TEXT FOR AI
        # ========================================

        context_texts = [

            item["text"]

            for item in relevant_chunks
        ]


        # ========================================
        # GENERATE AI ANSWER
        # ========================================

        answer = generate_answer(
            question,
            context_texts
        )


        # ========================================
        # RETURN ANSWER + SOURCES
        # ========================================

        return {

            "question":
                question,

            "answer":
                answer,

            "relevant_chunks":
                relevant_chunks
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Answer generation failed: {str(e)}"
        )
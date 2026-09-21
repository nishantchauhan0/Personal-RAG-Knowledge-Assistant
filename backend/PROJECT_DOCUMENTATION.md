# Personal RAG Knowledge Assistant

## 1. Project Introduction

Personal RAG Knowledge Assistant is a document-based question-answering application.

The application allows users to upload documents such as PDF and DOCX files and ask questions about their content.

The system uses Retrieval-Augmented Generation (RAG) to find relevant information from uploaded documents and generate answers using a local Large Language Model.

---

## 2. Project Objective

The main objectives of this project are:

* Upload PDF and DOCX documents.
* Extract text from uploaded documents.
* Divide large documents into smaller chunks.
* Convert text chunks into vector embeddings.
* Store embeddings in ChromaDB.
* Retrieve relevant information according to the user's question.
* Generate answers using a local AI model.
* Display the answer and relevant document sources in the frontend.

---

## 3. Technologies Used

### Backend

* Python
* FastAPI
* Uvicorn

### Document Processing

* pypdf
* python-docx

### RAG Components

* Sentence Transformers
* all-MiniLM-L6-v2
* ChromaDB

### AI Model

* Ollama
* Llama 3.2 3B

### Frontend

* HTML
* CSS
* JavaScript

### Development Tools

* Visual Studio Code
* Git
* GitHub

---

## 4. Project Structure

```text
Personal-RAG-Knowledge-Assistant/
│
├── backend/
│   ├── main.py
│   ├── document_loader.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   └── generator.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── documents/
│
├── chroma_db/
│
├── .env
├── .gitignore
├── requirements.txt
│
├── PROJECT_DOCUMENTATION.md
└── PROJECT_STRUCTURE.md
```

---

## 5. Backend Components

### 5.1 main.py

`main.py` is the main FastAPI application file.

It provides the following APIs:

### GET /

Checks whether the backend application is running.

### GET /health

Returns the health status of the backend.

### POST /upload

Uploads a PDF or DOCX document and processes it.

The document is:

1. Saved to the documents folder.
2. Converted into text.
3. Divided into chunks.
4. Converted into embeddings.
5. Stored in ChromaDB.

### POST /ask

Receives a user's question.

The question is passed to the retrieval system, relevant chunks are found, and the local AI model generates the final answer.

---

## 6. Document Loading

The `document_loader.py` file is responsible for extracting text from uploaded documents.

The project supports:

* PDF
* DOCX

For PDF files, `pypdf` is used.

For DOCX files, `python-docx` is used.

The extracted text is then passed to the chunking system.

---

## 7. Text Chunking

The `chunker.py` file divides large document text into smaller sections called chunks.

The project uses approximately:

* Chunk size: 1200 characters
* Overlap: 150 characters

Chunking helps the retrieval system search smaller and more relevant sections instead of processing the complete document every time.

---

## 8. Embeddings

The `embeddings.py` file converts text into numerical vector representations.

The project uses:

```text
all-MiniLM-L6-v2
```

from Sentence Transformers.

The same embedding process is used for:

* Document chunks
* User questions

This allows the system to compare the question with stored document information.

---

## 9. Vector Database

The project uses **ChromaDB** as the vector database.

ChromaDB stores:

* Document chunks
* Vector embeddings
* Document metadata

When a user asks a question, ChromaDB searches for the most relevant chunks.

---

## 10. Retrieval System

The `retriever.py` file is responsible for finding relevant information.

The process is:

```text
User Question
      ↓
Question Embedding
      ↓
ChromaDB Search
      ↓
Relevant Document Chunks
      ↓
Context for AI Model
```

The retriever also helps prioritize relevant sections for specific types of questions.

---

## 11. Local AI Model

The project uses Ollama to run the AI model locally.

The model used is:

```text
llama3.2:3b
```

The generator receives:

* User question
* Retrieved document context

The AI model then generates an answer using the retrieved information.

The system is instructed not to invent information that is not present in the retrieved document context.

---

## 12. RAG Working Process

The complete RAG pipeline works as follows:

```text
          USER
            │
            ▼
     Upload Document
            │
            ▼
      Text Extraction
            │
            ▼
        Chunking
            │
            ▼
      Text Embeddings
            │
            ▼
        ChromaDB
            │
            │
            ▼
      User Question
            │
            ▼
   Question Embedding
            │
            ▼
     Relevant Chunks
            │
            ▼
      Local LLM
       Ollama
            │
            ▼
        Final Answer
            │
            ▼
        Frontend
```

---

## 13. Frontend

The frontend is developed using:

* HTML
* CSS
* JavaScript

The frontend provides:

### Document Upload

Users can select a PDF or DOCX file and upload it.

### Question Input

Users can type questions about the uploaded document.

### Answer Display

The generated answer is displayed in the chat interface.

### Source Display

The application also displays the document chunks used to generate the answer.

This makes the RAG system more transparent because users can see where the information came from.

---

## 14. Complete RAG Flow

The complete working flow is:

### Step 1

User uploads a document.

### Step 2

FastAPI receives the document.

### Step 3

The document loader extracts the text.

### Step 4

The chunker divides the text into smaller chunks.

### Step 5

Sentence Transformers converts the chunks into embeddings.

### Step 6

The embeddings and chunks are stored in ChromaDB.

### Step 7

User asks a question.

### Step 8

The question is converted into an embedding.

### Step 9

ChromaDB searches for the most relevant chunks.

### Step 10

The retrieved chunks are sent as context to the local LLM.

### Step 11

Ollama generates the answer.

### Step 12

The frontend displays the answer and relevant sources.

---

## 15. Why RAG is Used

A normal AI model may not know the contents of a user's private document.

RAG solves this problem by retrieving relevant information from the uploaded document before generating the answer.

Therefore, the system can answer questions based on the user's own documents.

---

## 16. Example

Suppose a user uploads a resume.

The user can ask:

```text
What are my technical skills?
```

The system searches the resume for relevant information.

It may retrieve a chunk containing:

```text
Frontend: HTML, CSS, React.js
Backend: Node.js, Express.js
Database: MongoDB
```

The retrieved information is provided to the AI model.

The AI then generates the final answer.

The frontend also shows the source chunk used for the answer.

---

## 17. Running the Project

First activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Then start the backend:

```powershell
uvicorn backend.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

The API documentation can be accessed through:

```text
http://127.0.0.1:8000/docs
```

---

## 18. Testing

The project can be tested using the following questions after uploading a document:

```text
What are the main objectives?

What technologies are used?

What are the software requirements?

What are the main features?

What is the project methodology?
```

For a resume, example questions include:

```text
What are my technical skills?

What projects have I worked on?

What is my educational qualification?

Which programming languages are mentioned?

What technologies are used in my projects?
```

---

## 19. Advantages

* Uses user-provided documents.
* Supports PDF and DOCX files.
* Uses semantic search.
* Uses vector embeddings.
* Uses ChromaDB for retrieval.
* Uses a local AI model.
* Provides document sources.
* Reduces dependency on cloud AI APIs.
* Can be extended with additional features.

---

## 20. Future Improvements

Possible future improvements include:

* Better document parsing.
* Support for more document formats.
* Improved retrieval accuracy.
* Conversation memory.
* Multiple document management.
* User authentication.
* Cloud deployment.
* Better UI/UX.
* Streaming AI responses.
* Advanced source citations.

---

## 21. Project Status

The basic Personal RAG Knowledge Assistant is implemented and working.

The current system supports:

* PDF upload
* DOCX upload
* Text extraction
* Text chunking
* Embeddings
* ChromaDB storage
* Semantic retrieval
* Local LLM generation
* Question answering
* Source display

The next major step is deployment of the backend and frontend.

---

## 22. Conclusion

The Personal RAG Knowledge Assistant demonstrates how Retrieval-Augmented Generation can be used to build a document-based AI assistant.

The system combines document processing, vector embeddings, semantic retrieval, a vector database, and a local Large Language Model.

Users can upload their own documents and ask questions about their content.

This project provides practical experience with Python, FastAPI, RAG architecture, vector databases, embeddings, local AI models, and frontend development.

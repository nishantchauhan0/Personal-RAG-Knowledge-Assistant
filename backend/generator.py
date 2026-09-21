from openai import OpenAI


# Connect to local Ollama server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


def generate_answer(
    question: str,
    context: list[str]
) -> str:
    """
    Generate an answer using the local Ollama LLM.

    The answer must be based only on the retrieved
    document context.
    """

    context_text = "\n\n--- DOCUMENT CHUNK ---\n\n".join(
        context
    )

    prompt = f"""
You are a document question-answering assistant.

Your job is to answer the user's question using ONLY
the information present in the provided document context.

IMPORTANT RULES:

1. Do not use outside knowledge.
2. Do not invent information.
3. Do not add technologies that are not mentioned
   in the retrieved context.
4. If the document gives alternatives such as
   "FastAPI or Flask", do not choose one unless
   the document clearly identifies the selected one.
5. Do not confuse hardware requirements with
   software technologies.
6. For a question about technologies or software,
   focus on the Software Requirements / Technologies
   section rather than Processor, RAM, Storage,
   Display, or other hardware information.
7. Give a concise and clear answer.
8. If the context does not contain enough information,
   say:
   "I could not find the complete answer in the uploaded document."

DOCUMENT CONTEXT:

{context_text}

USER QUESTION:

{question}

ANSWER:
"""

    response = client.chat.completions.create(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    return response.choices[0].message.content.strip()
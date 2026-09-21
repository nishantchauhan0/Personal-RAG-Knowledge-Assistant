import os

from dotenv import load_dotenv
from openai import OpenAI


# Load variables from .env
load_dotenv()


api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing. "
        "Please add GROQ_API_KEY to the .env file."
    )


client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)


def generate_answer(
    question: str,
    context: list[str]
) -> str:
    """
    Generate an answer using Groq.

    The answer must be based only on the
    retrieved document context.
    """

    context_text = (
        "\n\n--- DOCUMENT CHUNK ---\n\n"
        .join(context)
    )

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the
information present in the document context.

Rules:

1. Do not use outside knowledge.
2. Do not invent information.
3. Do not add information that is not present
   in the document.
4. If the context does not contain enough information,
   say:
   "I could not find the complete answer in the uploaded document."
5. Give a clear and concise answer.

DOCUMENT CONTEXT:

{context_text}

USER QUESTION:

{question}

ANSWER:
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    return response.choices[0].message.content.strip()
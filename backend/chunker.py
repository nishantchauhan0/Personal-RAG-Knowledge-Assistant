import re


def split_text(text: str, chunk_size: int = 1200, overlap: int = 150):
    """
    Split document text into cleaner overlapping chunks.

    The function:
    - Cleans unnecessary spaces
    - Detects paragraphs
    - Keeps chunks reasonably small
    - Uses a smaller overlap to reduce repetition
    """

    # ========================================
    # CLEAN TEXT
    # ========================================

    text = text.replace("\r", "")
    text = text.strip()

    if not text:
        return []


    # ========================================
    # NORMALIZE EXCESSIVE BLANK LINES
    # ========================================

    text = re.sub(r"\n\s*\n+", "\n\n", text)


    # ========================================
    # SPLIT INTO PARAGRAPHS
    # ========================================

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]


    chunks = []
    current_chunk = ""


    # ========================================
    # CREATE BASE CHUNKS
    # ========================================

    for paragraph in paragraphs:

        # If paragraph itself is larger than chunk size
        if len(paragraph) > chunk_size:

            # Save current chunk first
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            # Split large paragraph into smaller pieces
            start = 0

            while start < len(paragraph):

                end = start + chunk_size

                piece = paragraph[start:end].strip()

                if piece:
                    chunks.append(piece)

                start = end

            continue


        # Add paragraph to current chunk
        if (
            len(current_chunk) +
            len(paragraph) +
            2
            <= chunk_size
        ):

            if current_chunk:
                current_chunk += "\n\n"

            current_chunk += paragraph

        else:

            # Store completed chunk
            if current_chunk:
                chunks.append(
                    current_chunk.strip()
                )

            # Start new chunk
            current_chunk = paragraph


    # ========================================
    # ADD FINAL CHUNK
    # ========================================

    if current_chunk:
        chunks.append(
            current_chunk.strip()
        )


    # ========================================
    # CREATE SMALL OVERLAP
    # ========================================

    final_chunks = []

    for i, chunk in enumerate(chunks):

        if i == 0:

            final_chunks.append(chunk)

            continue


        previous_chunk = chunks[i - 1]

        # Take only a small amount from
        # the end of previous chunk
        overlap_text = previous_chunk[-overlap:]


        combined_chunk = (
            overlap_text +
            "\n\n" +
            chunk
        )


        final_chunks.append(
            combined_chunk.strip()
        )


    return final_chunks

const API_URL = "http://127.0.0.1:8000";

console.log("RAG SCRIPT FINAL V5 LOADED");


// ========================================
// ELEMENTS
// ========================================

const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

const questionInput = document.getElementById("questionInput");
const askBtn = document.getElementById("askBtn");
const answer = document.getElementById("answer");


// ========================================
// CLEAR INITIAL PLACEHOLDER
// ========================================

function clearPlaceholder() {

    const placeholder = answer.querySelector(".placeholder");

    if (placeholder) {
        placeholder.remove();
    }

    if (
        answer.childNodes.length === 1 &&
        answer.textContent.trim() === "Your answer will appear here..."
    ) {
        answer.textContent = "";
    }
}


// ========================================
// UPLOAD DOCUMENT
// ========================================

uploadBtn.addEventListener("click", async function () {

    const file = fileInput.files[0];

    if (!file) {

        uploadStatus.textContent =
            "⚠️ Please select a PDF or DOCX file first.";

        return;
    }

    uploadStatus.textContent =
        "⏳ Uploading and processing document...";

    uploadBtn.disabled = true;
    uploadBtn.textContent = "Processing...";

    const formData = new FormData();

    formData.append("file", file);

    try {

        const response = await fetch(
            API_URL + "/upload",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (response.ok) {

            uploadStatus.textContent =
                "✅ " +
                data.message +
                " | " +
                data.chunks_created +
                " chunks created.";

            fileInput.value = "";

        } else {

            uploadStatus.textContent =
                "❌ " +
                (data.detail || "Upload failed.");
        }

    } catch (error) {

        console.error("Upload Error:", error);

        uploadStatus.textContent =
            "❌ Backend connection failed. Make sure the server is running.";

    } finally {

        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload Document";
    }

});


// ========================================
// ASK QUESTION
// ========================================

askBtn.addEventListener("click", async function () {

    const question = questionInput.value.trim();

    if (!question) {

        addErrorMessage(
            "⚠️ Please enter a question."
        );

        return;
    }

    clearPlaceholder();

    addUserMessage(question);

    const thinkingMessage = addThinkingMessage();

    questionInput.value = "";

    askBtn.disabled = true;
    askBtn.textContent = "Thinking...";

    try {

        const controller = new AbortController();

        const timeout = setTimeout(
            function () {
                controller.abort();
            },
            120000
        );

        const response = await fetch(
            API_URL + "/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                }),

                signal: controller.signal
            }
        );

        clearTimeout(timeout);

        const responseText = await response.text();

        let data;

        try {

            data = JSON.parse(responseText);

        } catch (jsonError) {

            console.error(
                "Invalid JSON response:",
                responseText
            );

            throw new Error(
                "Backend returned an invalid response."
            );
        }

        console.log("Backend response:", data);

        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        if (response.ok) {

            addAIMessage(
                data.answer,
                data.relevant_chunks || []
            );

        } else {

            addErrorMessage(
                "❌ " +
                (
                    data.detail ||
                    "Something went wrong."
                )
            );
        }

    } catch (error) {

        console.error(
            "Question Error:",
            error
        );

        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        if (error.name === "AbortError") {

            addErrorMessage(
                "❌ The AI response took too long. Please try again."
            );

        } else {

            addErrorMessage(
                "❌ Backend connection failed. Make sure the server is running."
            );
        }

    } finally {

        askBtn.disabled = false;
        askBtn.textContent = "Ask Question";

        questionInput.focus();
    }

});


// ========================================
// ENTER KEY SUPPORT
// ========================================

questionInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            askBtn.click();
        }
    }
);


// ========================================
// ADD USER MESSAGE
// ========================================

function addUserMessage(question) {

    const message =
        document.createElement("div");

    message.className =
        "message user-message";

    message.innerHTML = `

        <div class="message-icon">
            👤
        </div>

        <div class="message-content">

            <strong>
                You
            </strong>

            <p>
                ${escapeHTML(question)}
            </p>

        </div>

    `;

    answer.appendChild(message);

    scrollToLatestMessage();
}


// ========================================
// ADD THINKING MESSAGE
// ========================================

function addThinkingMessage() {

    const message =
        document.createElement("div");

    message.className =
        "message ai-message";

    message.innerHTML = `

        <div class="message-icon">
            🤖
        </div>

        <div class="message-content">

            <strong>
                AI Assistant
            </strong>

            <p>
                ⏳ Thinking...
            </p>

        </div>

    `;

    answer.appendChild(message);

    scrollToLatestMessage();

    return message;
}


// ========================================
// FORMAT AI ANSWER
// ========================================

function formatAIAnswer(text) {

    if (!text) {
        return "";
    }

    /*
        IMPORTANT:

        First convert the AI response into plain
        HTML-safe text.

        Then process Markdown patterns.
    */

    let formatted = escapeHTML(
        String(text)
    );

    formatted = formatted.replace(
        /\r\n/g,
        "\n"
    );

    formatted = formatted.replace(
        /\r/g,
        "\n"
    );


    // ========================================
    // REMOVE MARKDOWN HEADINGS
    // ========================================

    formatted = formatted.replace(
        /(^|\n)\s*#{1,6}\s+(.+?)(?=\n|$)/g,
        '$1<div class="markdown-heading">$2</div>'
    );


    // ========================================
    // NUMBERING
    // Handles:
    //
    // **1.** Text
    // **1**. Text
    // ========================================

    formatted = formatted.replace(
        /\*\*\s*(\d+)\s*\.\s*\*\*/g,
        "<strong>$1.</strong>"
    );

    formatted = formatted.replace(
        /\*\*\s*(\d+)\s*\*\*\s*\./g,
        "<strong>$1.</strong>"
    );


    // ========================================
    // NORMAL NUMBERING
    // ========================================

    formatted = formatted.replace(
        /(^|\n)\s*(\d+)\.\s+/g,
        '$1<strong>$2.</strong> '
    );


    // ========================================
    // BOLD
    // Handles:
    //
    // **text**
    // ========================================

    formatted = formatted.replace(
        /\*\*(.+?)\*\*/g,
        "<strong>$1</strong>"
    );


    // ========================================
    // ITALIC
    // ========================================

    formatted = formatted.replace(
        /(^|[\s(])\*([^*\n]+)\*(?=[\s).,!?:;]|$)/g,
        "$1<em>$2</em>"
    );


    // ========================================
    // BULLETS
    // ========================================

    formatted = formatted.replace(
        /(^|\n)\s*[•●▪◦]\s*/g,
        "$1• "
    );


    // ========================================
    // DASH BULLETS
    // ========================================

    formatted = formatted.replace(
        /(^|\n)\s*[-*]\s+/g,
        "$1• "
    );


    // ========================================
    // REMOVE REMAINING MARKDOWN SYMBOLS
    // ========================================

    formatted = formatted.replace(
        /\*\*/g,
        ""
    );

    formatted = formatted.replace(
        /(^|\n)\s*#{1,6}\s*/g,
        "$1"
    );


    // ========================================
    // CLEAN EXTRA SPACES
    // ========================================

    formatted = formatted.replace(
        /[ \t]+\n/g,
        "\n"
    );


    // ========================================
    // LINE BREAKS
    // ========================================

    formatted = formatted.replace(
        /\n/g,
        "<br>"
    );


    // ========================================
    // FIX HEADING BREAKS
    // ========================================

    formatted = formatted.replace(
        /<br>\s*<div class="markdown-heading">/g,
        '<div class="markdown-heading">'
    );


    // ========================================
    // REMOVE EXTRA BREAKS
    // ========================================

    formatted = formatted.replace(
        /(<br>\s*){3,}/g,
        "<br><br>"
    );


    // ========================================
    // REMOVE BREAKS AT START
    // ========================================

    formatted = formatted.replace(
        /^(<br>\s*)+/,
        ""
    );


    return formatted.trim();
}


// ========================================
// CLEAN SOURCE TEXT
// ========================================

function cleanSourceText(text) {

    if (!text) {
        return "";
    }

    let cleaned =
        String(text);

    cleaned = cleaned.replace(
        /\s+/g,
        " "
    );

    cleaned = cleaned.replace(
        /^hat retrieved/i,
        "That retrieved"
    );

    cleaned = cleaned.replace(
        /\*\*/g,
        ""
    );

    cleaned = cleaned.replace(
        /#{1,6}\s*/g,
        ""
    );

    return cleaned.trim();
}


// ========================================
// CREATE SOURCE KEY
// ========================================

function getSourceKey(source) {

    if (typeof source === "string") {
        return source.trim();
    }

    return (
        (source.document_name || "") +
        "|" +
        (source.chunk_index ?? "") +
        "|" +
        (source.text || "")
    ).trim();
}


// ========================================
// ADD AI MESSAGE
// ========================================

function addAIMessage(
    answerText,
    sources
) {

    const message =
        document.createElement("div");

    message.className =
        "message ai-message";

    const formattedAnswer =
        formatAIAnswer(answerText);

    message.innerHTML = `

        <div class="message-icon">
            🤖
        </div>

        <div class="message-content">

            <strong>
                AI Assistant
            </strong>

            <div class="formatted-answer">
                ${formattedAnswer}
            </div>

        </div>

    `;

    answer.appendChild(message);


    // ========================================
    // SOURCES
    // ========================================

    if (
        sources &&
        sources.length > 0
    ) {

        const sourcesBox =
            document.createElement("div");

        sourcesBox.className =
            "sources";


        // ========================================
        // REMOVE DUPLICATE SOURCES
        // ========================================

        const uniqueSources = [];

        const sourceKeys =
            new Set();

        sources.forEach(
            function (source) {

                const key =
                    getSourceKey(source);

                if (
                    key &&
                    !sourceKeys.has(key)
                ) {

                    sourceKeys.add(key);

                    uniqueSources.push(
                        source
                    );
                }
            }
        );


        let sourcesHTML = `

            <h4>
                📚 Sources Used
            </h4>

        `;


        // ========================================
        // DISPLAY SOURCES
        // ========================================

        uniqueSources.forEach(
            function (source) {

                const rawSourceText =
                    typeof source === "string"
                        ? source
                        : source.text || "";

                const sourceText =
                    cleanSourceText(
                        rawSourceText
                    );


                const documentName =
                    typeof source === "object" &&
                    source.document_name
                        ? source.document_name
                        : "Unknown Document";


                const chunkIndex =
                    typeof source === "object"
                        ? source.chunk_index
                        : null;


                let sourceLabel =
                    "📄 " +
                    escapeHTML(
                        documentName
                    );


                if (
                    chunkIndex !== null &&
                    chunkIndex !== undefined
                ) {

                    sourceLabel +=
                        " • Chunk " +
                        (
                            Number(chunkIndex) + 1
                        );
                }


                const preview =
                    sourceText.length > 900
                        ? sourceText.substring(
                            0,
                            900
                        ) + "..."
                        : sourceText;


                sourcesHTML += `

                    <div class="source-item">

                        <strong>
                            ${sourceLabel}
                        </strong>

                        <p>
                            ${escapeHTML(preview)}
                        </p>

                    </div>

                `;
            }
        );


        sourcesBox.innerHTML =
            sourcesHTML;

        answer.appendChild(
            sourcesBox
        );
    }


    scrollToLatestMessage();
}


// ========================================
// ADD ERROR MESSAGE
// ========================================

function addErrorMessage(
    messageText
) {

    clearPlaceholder();

    const message =
        document.createElement("div");

    message.className =
        "message error-message";

    message.innerHTML = `

        <div class="message-content">

            <strong>
                Error
            </strong>

            <p>
                ${escapeHTML(messageText)}
            </p>

        </div>

    `;

    answer.appendChild(message);

    scrollToLatestMessage();
}


// ========================================
// AUTO SCROLL
// ========================================

function scrollToLatestMessage() {

    answer.scrollTop =
        answer.scrollHeight;
}


// ========================================
// SECURITY
// ========================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent =
        String(text);

    return div.innerHTML;
}


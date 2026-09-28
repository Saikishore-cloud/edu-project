/**
 * ==========================================================================
 * EDUGENIE – AI LEARNING ASSISTANT FRONTEND CONTROLLER
 * Full client-side architecture for task switching, API communication,
 * markdown parsing, interactive quiz grading, toasts, and UI states.
 * ==========================================================================
 */

// Global API Base URL & Task State
const API_BASE_URL = "";
let currentTask = "qa";
let currentQuizData = [];
let currentRawResult = "";
let lastSubmittedPrompt = "";

// Task Configuration Metadata (Placeholders, Labels, Examples, Endpoints)
const TASK_CONFIG = {
    qa: {
        title: "Ask EduGenie a Question",
        subtitle: "Type any academic question to receive clear, direct explanations",
        placeholder: "e.g., Which is the largest ocean? How do plants convert sunlight into food?",
        endpoint: "/qa",
        examples: [
            "Which is the largest ocean?",
            "Why is the sky blue?",
            "What is the speed of light?",
            "Explain Newton's third law of motion"
        ]
    },
    explain: {
        title: "Concept Explainer",
        subtitle: "Understand complex topics through intuitive real-world analogies",
        placeholder: "e.g., Explain Quantum Superposition, the Pythagorean Theorem, or Photosynthesis...",
        endpoint: "/explain",
        examples: [
            "Explain Photosynthesis with an analogy",
            "Pythagorean Theorem and proofs",
            "How does Blockchain work?",
            "Explain Big-O notation simply"
        ]
    },
    quiz: {
        title: "AI Quiz Generator",
        subtitle: "Generate multiple-choice practice questions with instant grading",
        placeholder: "e.g., Python programming basics, Solar system planets, World War II timeline...",
        endpoint: "/quiz",
        examples: [
            "Python programming fundamentals",
            "Solar system and planets",
            "Photosynthesis & Plant Biology",
            "SQL Database queries"
        ]
    },
    summarize: {
        title: "Smart Educational Summarizer",
        subtitle: "Paste articles, chapters, or lecture notes to extract key takeaways",
        placeholder: "Paste an article, study guide, or paragraph here to generate a concise summary...",
        endpoint: "/summarize",
        examples: [
            "Photosynthesis is the process used by plants, algae, and certain bacteria to harness energy from sunlight and turn it into chemical energy. Light energy transfers electrons from water to carbon dioxide, producing glucose and releasing vital oxygen into the atmosphere.",
            "The Industrial Revolution marked a period of development in the latter half of the 18th century that transformed largely rural, agrarian societies in Europe and America into industrialized, urban ones."
        ]
    },
    learn: {
        title: "Personalized Learning Path",
        subtitle: "Build a structured roadmap from beginner to advanced mastery",
        placeholder: "e.g., Python for Data Science, Full Stack Web Development, Quantum Physics...",
        endpoint: "/learn/recommendations",
        examples: [
            "Python for Beginners to Advanced",
            "Machine Learning Engineer Roadmap",
            "Full Stack Web Development in 2026",
            "Data Structures and Algorithms"
        ]
    }
};

/**
 * Initialize application when DOM is fully loaded
 */
document.addEventListener("DOMContentLoaded", () => {
    // Initialize default task UI
    selectTask("qa");

    // Global keyboard shortcut: Ctrl+Enter or Cmd+Enter to generate
    const userInput = document.getElementById("userInput");
    if (userInput) {
        userInput.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                submitTask();
            }
        });
    }

    // Update active nav links on scroll
    initScrollSpy();
});

/**
 * Task Selection Handler
 * Updates tabs, title, subtitle, placeholder, example chips, and char counter.
 * @param {string} task - Target task ('qa', 'explain', 'quiz', 'summarize', 'learn')
 */
function selectTask(task) {
    if (!TASK_CONFIG[task]) return;
    currentTask = task;

    // Update active tab buttons
    const allTabs = document.querySelectorAll(".task-tab");
    allTabs.forEach(tab => {
        const isMatch = tab.getAttribute("data-task") === task;
        tab.classList.toggle("active", isMatch);
        tab.setAttribute("aria-selected", isMatch ? "true" : "false");
    });

    const config = TASK_CONFIG[task];

    // Update UI Titles and Placeholders
    const inputTitle = document.getElementById("inputTitle");
    const inputSubtitle = document.getElementById("inputSubtitle");
    const userInput = document.getElementById("userInput");

    if (inputTitle) inputTitle.textContent = config.title;
    if (inputSubtitle) inputSubtitle.textContent = config.subtitle;
    if (userInput) {
        userInput.placeholder = config.placeholder;
    }

    // Populate Example Suggestion Chips
    renderExampleChips(config.examples);

    // Update character counter
    updateCharacterCount();
}

/**
 * Render quick-fill example chips
 * @param {string[]} examples - Array of sample prompts
 */
function renderExampleChips(examples) {
    const container = document.getElementById("exampleChips");
    if (!container) return;

    container.innerHTML = "";
    examples.forEach(text => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "btn-chip";
        chip.textContent = text.length > 40 ? text.substring(0, 38) + "..." : text;
        chip.title = text;
        chip.addEventListener("click", () => {
            const input = document.getElementById("userInput");
            if (input) {
                input.value = text;
                updateCharacterCount();
                input.focus();
            }
        });
        container.appendChild(chip);
    });
}

/**
 * Update textarea character count indicator
 */
function updateCharacterCount() {
    const input = document.getElementById("userInput");
    const counter = document.getElementById("charCounter");
    if (!input || !counter) return;

    const len = input.value.length;
    counter.textContent = `${len} / 4000 characters`;
    if (len > 3800) {
        counter.style.color = "#f87171";
    } else {
        counter.style.color = "";
    }
}

/**
 * Smoothly scroll the page to the AI Workspace section
 */
function scrollToWorkspace() {
    const workspace = document.getElementById("workspace");
    if (workspace) {
        workspace.scrollIntoView({ behavior: "smooth", block: "start" });
        const input = document.getElementById("userInput");
        if (input) {
            setTimeout(() => input.focus(), 400);
        }
    }
}

/**
 * Toggle mobile drawer menu navigation
 */
function toggleMobileMenu() {
    const drawer = document.getElementById("mobileDrawer");
    if (drawer) {
        drawer.classList.toggle("open");
    }
}

/**
 * Main submit function to send user prompt to backend
 */
async function submitTask() {
    const userInput = document.getElementById("userInput");
    if (!userInput) return;

    const inputVal = userInput.value.trim();
    if (!inputVal) {
        showError("Please enter your question, topic, or study notes before generating.");
        userInput.focus();
        return;
    }

    lastSubmittedPrompt = inputVal;
    showLoading();

    try {
        let responseData = null;
        let isSuccess = false;

        // Primary API endpoint: /api/generate
        try {
            const primaryRes = await fetch(`${API_BASE_URL}/api/generate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    task: currentTask,
                    prompt: inputVal,
                    input: inputVal
                })
            });

            if (primaryRes.ok) {
                responseData = await primaryRes.json();
                isSuccess = true;
            } else if (primaryRes.status !== 404) {
                const errJson = await primaryRes.json().catch(() => ({}));
                throw new Error(errJson.error || errJson.message || `Server error (${primaryRes.status})`);
            }
        } catch (primErr) {
            // If primary endpoint failed not because of 404, capture error
            if (!primErr.message.includes("404")) {
                console.warn("Primary /api/generate route notice:", primErr.message);
            }
        }

        // Resilient Fallback: If /api/generate was 404 or missing, route to feature endpoint (/qa, /explain, /quiz, /summarize, /learn/recommendations)
        if (!isSuccess) {
            const config = TASK_CONFIG[currentTask];
            const fallbackEndpoint = config ? config.endpoint : `/${currentTask}`;
            
            const fallbackRes = await fetch(`${API_BASE_URL}${fallbackEndpoint}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    input: inputVal,
                    prompt: inputVal,
                    task: currentTask
                })
            });

            if (!fallbackRes.ok) {
                const errData = await fallbackRes.json().catch(() => ({}));
                throw new Error(errData.error || errData.message || `Server returned error (${fallbackRes.status})`);
            }

            responseData = await fallbackRes.json();
        }

        hideLoading();
        showResult(responseData);

    } catch (error) {
        hideLoading();
        showError(
            error.message || "Failed to communicate with the EduGenie backend server. Please check your connection."
        );
    }
}

/**
 * Display backend response data (Handles text, structured quiz JSON, or questions array)
 * @param {object|string} data - Response from API
 */
function showResult(data) {
    hideError();
    const resultBox = document.getElementById("resultBox");
    const textWrap = document.getElementById("textContentWrap");
    const quizWrap = document.getElementById("quizContentWrap");
    const resultTitle = document.getElementById("resultTaskTitle");

    if (!resultBox) return;

    // Set Task Title
    if (resultTitle) {
        const titles = {
            qa: "AI Q&A Answer",
            explain: "Concept Explanation",
            quiz: "Interactive Practice Quiz",
            summarize: "Key Summary & Takeaways",
            learn: "Custom Learning Roadmap"
        };
        resultTitle.textContent = titles[currentTask] || "AI Generated Output";
    }

    // Check if task is QUIZ and questions are provided
    if (currentTask === "quiz") {
        let questions = null;

        if (data && Array.isArray(data.questions)) {
            questions = data.questions;
        } else if (data && typeof data.result === "string") {
            // Attempt to parse structured JSON from result string
            try {
                const cleaned = cleanJsonString(data.result);
                const parsed = JSON.parse(cleaned);
                if (Array.isArray(parsed)) {
                    questions = parsed;
                } else if (parsed && Array.isArray(parsed.questions)) {
                    questions = parsed.questions;
                }
            } catch (e) {
                // Graceful fallback to formatted text if quiz is not JSON
                questions = null;
            }
        }

        if (questions && questions.length > 0) {
            renderQuiz(questions);
            if (textWrap) textWrap.style.display = "none";
            if (quizWrap) quizWrap.style.display = "flex";
            resultBox.style.display = "block";
            resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
            return;
        }
    }

    // Normal Text Result Rendering (Q&A, Explain, Summarize, Learn, or text-fallback Quiz)
    let contentString = "";
    if (typeof data === "string") {
        contentString = data;
    } else if (data && typeof data.result === "string") {
        contentString = data.result;
    } else if (data && data.text) {
        contentString = data.text;
    } else {
        contentString = JSON.stringify(data, null, 2);
    }

    currentRawResult = contentString;
    renderMarkdownResult(contentString);

    if (quizWrap) quizWrap.style.display = "none";
    if (textWrap) textWrap.style.display = "block";
    resultBox.style.display = "block";
    resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Render Markdown-like formatted content safely into the DOM
 * @param {string} raw - Raw text / markdown string
 */
function renderMarkdownResult(raw) {
    const container = document.getElementById("resultContent");
    if (!container) return;

    if (!raw || !raw.trim()) {
        container.innerHTML = "<p>No response content generated.</p>";
        return;
    }

    let html = escapeHtml(raw);

    // Code blocks: ```lang ... ```
    html = html.replace(/```([a-zA-Z0-9]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code class="language-${lang}">${code.trim()}</code></pre>`;
    });

    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Headings: ###, ##, #
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold: **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Italic: *text*
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Blockquotes: > quote
    html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');

    // Unordered lists: - item or * item
    html = html.replace(/^\s*[\-\*]\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gims, '<ul>$1</ul>');
    // Clean nested duplicate <ul> tags
    html = html.replace(/<\/ul>\s*<ul>/gim, '');

    // Numbered lists: 1. item
    html = html.replace(/^\s*\d+\.\s+(.*$)/gim, '<li class="num-item">$1</li>');

    // Paragraph breaks
    const paragraphs = html.split(/\n\s*\n/);
    const formatted = paragraphs.map(p => {
        const trimmed = p.trim();
        if (trimmed.startsWith('<h') || trimmed.startsWith('<pre') || trimmed.startsWith('<ul') || trimmed.startsWith('<blockquote')) {
            return trimmed;
        }
        return `<p>${trimmed.replace(/\n/g, '<br>')}</p>`;
    }).join('');

    container.innerHTML = formatted;
}

/**
 * Render interactive Multiple-Choice Practice Quiz
 * @param {Array} questions - Array of questions { question, options, answer }
 */
function renderQuiz(questions) {
    currentQuizData = questions;
    const list = document.getElementById("quizQuestionsList");
    const countBadge = document.getElementById("quizQuestionCountBadge");
    const scoreBanner = document.getElementById("quizScoreBanner");
    const submitBtn = document.getElementById("submitQuizBtn");

    if (!list) return;
    list.innerHTML = "";

    if (countBadge) {
        countBadge.textContent = `${questions.length} Questions Available`;
    }

    if (scoreBanner) scoreBanner.style.display = "none";
    if (submitBtn) {
        submitBtn.style.display = "inline-flex";
        submitBtn.disabled = false;
    }

    questions.forEach((qItem, qIndex) => {
        const card = document.createElement("div");
        card.className = "quiz-card";
        card.id = `quizCard_${qIndex}`;

        const header = document.createElement("div");
        header.className = "quiz-question-header";

        const numBadge = document.createElement("span");
        numBadge.className = "quiz-q-num";
        numBadge.textContent = `Q${qIndex + 1}`;

        const qText = document.createElement("div");
        qText.className = "quiz-q-text";
        qText.textContent = qItem.question || `Question ${qIndex + 1}`;

        header.appendChild(numBadge);
        header.appendChild(qText);
        card.appendChild(header);

        const optionsGroup = document.createElement("div");
        optionsGroup.className = "quiz-options-group";

        const options = Array.isArray(qItem.options) ? qItem.options : [];
        options.forEach((optText, optIndex) => {
            const label = document.createElement("label");
            label.className = "quiz-option-label";
            label.id = `q${qIndex}_opt${optIndex}_label`;

            const radio = document.createElement("input");
            radio.type = "radio";
            radio.name = `quiz_q_${qIndex}`;
            radio.value = optIndex;

            radio.addEventListener("change", () => {
                const allLabels = card.querySelectorAll(".quiz-option-label");
                allLabels.forEach(l => l.classList.remove("selected"));
                label.classList.add("selected");
            });

            const textSpan = document.createElement("span");
            const letterPrefix = String.fromCharCode(65 + optIndex);
            textSpan.textContent = `${letterPrefix}. ${optText}`;

            label.appendChild(radio);
            label.appendChild(textSpan);
            optionsGroup.appendChild(label);
        });

        card.appendChild(optionsGroup);
        list.appendChild(card);
    });
}

/**
 * Submit and Grade Quiz Answers
 */
function submitQuiz() {
    if (!currentQuizData || currentQuizData.length === 0) return;

    // Check if every question has been answered
    let allAnswered = true;
    let firstUnansweredCard = null;

    for (let i = 0; i < currentQuizData.length; i++) {
        const checked = document.querySelector(`input[name="quiz_q_${i}"]:checked`);
        if (!checked) {
            allAnswered = false;
            if (!firstUnansweredCard) {
                firstUnansweredCard = document.getElementById(`quizCard_${i}`);
            }
        }
    }

    if (!allAnswered) {
        showError("Please answer all quiz questions before submitting.");
        if (firstUnansweredCard) {
            firstUnansweredCard.scrollIntoView({ behavior: "smooth", block: "center" });
        }
        return;
    }

    hideError();

    // Grade each question
    let score = 0;
    const total = currentQuizData.length;

    currentQuizData.forEach((qItem, qIndex) => {
        const card = document.getElementById(`quizCard_${qIndex}`);
        const selectedRadio = document.querySelector(`input[name="quiz_q_${qIndex}"]:checked`);
        const userSelected = selectedRadio ? parseInt(selectedRadio.value, 10) : -1;
        const correctIndex = parseInt(qItem.answer, 10);

        // Disable all radio buttons in this card
        const radios = card.querySelectorAll(`input[name="quiz_q_${qIndex}"]`);
        radios.forEach(r => (r.disabled = true));

        // Highlight correct option
        const correctLabel = document.getElementById(`q${qIndex}_opt${correctIndex}_label`);
        if (correctLabel) {
            correctLabel.classList.add("is-correct");
        }

        if (userSelected === correctIndex) {
            score++;
            card.classList.add("answered-correctly");
        } else {
            card.classList.add("answered-incorrectly");
            if (userSelected >= 0) {
                const wrongLabel = document.getElementById(`q${qIndex}_opt${userSelected}_label`);
                if (wrongLabel) {
                    wrongLabel.classList.add("is-incorrect");
                }
            }
        }
    });

    // Score calculations
    const percentage = ((score / total) * 100).toFixed(1);

    const scoreText = document.getElementById("scoreText");
    const percentageText = document.getElementById("percentageText");
    const scoreFeedback = document.getElementById("scoreFeedback");
    const scoreTrophy = document.getElementById("scoreTrophyIcon");
    const scoreHeadline = document.getElementById("scoreHeadline");

    if (scoreText) scoreText.textContent = `Your Score: ${score} / ${total}`;
    if (percentageText) percentageText.textContent = `Percentage: ${percentage}%`;

    if (score === total) {
        if (scoreHeadline) scoreHeadline.textContent = "Outstanding Performance! 🌟";
        if (scoreFeedback) scoreFeedback.textContent = "Perfect score! You have completely mastered this concept.";
        if (scoreTrophy) scoreTrophy.textContent = "🏆";
    } else if (score >= total / 2) {
        if (scoreHeadline) scoreHeadline.textContent = "Good Effort! 👍";
        if (scoreFeedback) scoreFeedback.textContent = "Solid score! Review the green highlighted answers to strengthen your understanding.";
        if (scoreTrophy) scoreTrophy.textContent = "🎖️";
    } else {
        if (scoreHeadline) scoreHeadline.textContent = "Keep Practicing! 📚";
        if (scoreFeedback) scoreFeedback.textContent = "Review the explanations above and retake the quiz to reinforce your knowledge.";
        if (scoreTrophy) scoreTrophy.textContent = "💡";
    }

    const banner = document.getElementById("quizScoreBanner");
    const submitBtn = document.getElementById("submitQuizBtn");

    if (banner) banner.style.display = "flex";
    if (submitBtn) submitBtn.style.display = "none";

    showToast(`Quiz completed! You scored ${score}/${total} (${percentage}%)`);
    banner.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Restart and retake the current practice quiz
 */
function restartQuiz() {
    if (!currentQuizData || currentQuizData.length === 0) return;
    renderQuiz(currentQuizData);
    showToast("Quiz reset. Good luck!");
}

/**
 * Copy result content to system clipboard
 */
async function copyResult() {
    let textToCopy = "";
    if (currentTask === "quiz" && currentQuizData.length > 0) {
        textToCopy = currentQuizData.map((q, idx) => {
            const opts = (q.options || []).map((o, i) => `  ${String.fromCharCode(65 + i)}. ${o}`).join("\n");
            return `Question ${idx + 1}: ${q.question}\n${opts}\nCorrect Answer: ${String.fromCharCode(65 + q.answer)}\n`;
        }).join("\n");
    } else {
        textToCopy = currentRawResult;
    }

    if (!textToCopy) {
        showToast("No content to copy.", "error");
        return;
    }

    try {
        await navigator.clipboard.writeText(textToCopy);
        const copyBtnText = document.getElementById("copyBtnText");
        if (copyBtnText) copyBtnText.textContent = "Copied!";
        showToast("Copied result to clipboard!");
        setTimeout(() => {
            if (copyBtnText) copyBtnText.textContent = "Copy";
        }, 2000);
    } catch (err) {
        showToast("Failed to copy to clipboard.", "error");
    }
}

/**
 * Regenerate current task with last submitted prompt
 */
function regenerateResult() {
    const input = document.getElementById("userInput");
    if (lastSubmittedPrompt && input) {
        input.value = lastSubmittedPrompt;
        updateCharacterCount();
        submitTask();
    } else {
        submitTask();
    }
}

/**
 * Clear textarea input
 */
function clearInput() {
    const input = document.getElementById("userInput");
    if (input) {
        input.value = "";
        updateCharacterCount();
        input.focus();
    }
    hideError();
}

/**
 * Clear result output
 */
function clearResult() {
    const resultBox = document.getElementById("resultBox");
    if (resultBox) {
        resultBox.style.display = "none";
    }
    currentRawResult = "";
    currentQuizData = [];
    hideError();
}

/**
 * Show animated AI loading state
 */
function showLoading() {
    hideError();
    const loadingBox = document.getElementById("loadingBox");
    const generateBtn = document.getElementById("generateBtn");
    const btnSpinner = document.getElementById("btnSpinner");
    const btnText = document.getElementById("generateBtnText");
    const statusText = document.getElementById("workspaceStatusText");

    if (loadingBox) loadingBox.style.display = "flex";
    if (generateBtn) generateBtn.disabled = true;
    if (btnSpinner) btnSpinner.style.display = "inline-block";
    if (btnText) btnText.textContent = "Thinking...";
    if (statusText) statusText.textContent = "AI Processing...";

    if (loadingBox) {
        loadingBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
}

/**
 * Hide loading state
 */
function hideLoading() {
    const loadingBox = document.getElementById("loadingBox");
    const generateBtn = document.getElementById("generateBtn");
    const btnSpinner = document.getElementById("btnSpinner");
    const btnText = document.getElementById("generateBtnText");
    const statusText = document.getElementById("workspaceStatusText");

    if (loadingBox) loadingBox.style.display = "none";
    if (generateBtn) generateBtn.disabled = false;
    if (btnSpinner) btnSpinner.style.display = "none";
    if (btnText) btnText.textContent = "Generate Response";
    if (statusText) statusText.textContent = "Ready for Prompts";
}

/**
 * Show error card with message
 * @param {string} msg - Error description
 */
function showError(msg) {
    const errorBox = document.getElementById("errorBox");
    const errorText = document.getElementById("errorText");

    if (errorText) errorText.textContent = msg;
    if (errorBox) {
        errorBox.style.display = "flex";
        errorBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
}

/**
 * Hide error card
 */
function hideError() {
    const errorBox = document.getElementById("errorBox");
    if (errorBox) errorBox.style.display = "none";
}

/**
 * Non-intrusive Toast Notification Popup
 * @param {string} message - Toast text
 * @param {string} type - 'success' or 'error'
 */
function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type === "error" ? "toast-error" : ""}`;
    toast.innerHTML = `<span>${type === "error" ? "⚠️" : "✦"}</span><span>${escapeHtml(message)}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("fade-out");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

/**
 * Helper to escape HTML characters
 */
function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * Clean markdown wrapper from JSON string
 */
function cleanJsonString(str) {
    if (!str) return "";
    let cleaned = str.trim();
    if (cleaned.startsWith("```")) {
        cleaned = cleaned.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
    }
    return cleaned;
}

/**
 * Active navigation scroll spy
 */
function initScrollSpy() {
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-link");

    window.addEventListener("scroll", () => {
        let currentSectionId = "";
        const scrollPos = window.scrollY + 120;

        sections.forEach(sec => {
            const top = sec.offsetTop;
            const height = sec.offsetHeight;
            if (scrollPos >= top && scrollPos < top + height) {
                currentSectionId = sec.getAttribute("id");
            }
        });

        navLinks.forEach(link => {
            link.classList.remove("active");
            if (link.getAttribute("href") === `#${currentSectionId}`) {
                link.classList.add("active");
            }
        });
    });
}

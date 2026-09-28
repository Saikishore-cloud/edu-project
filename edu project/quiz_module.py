"""
quiz_module.py - Quiz Generation Module for EduGenie
Generates exactly 3 multiple-choice questions with 4 options each,
parsing and validating JSON responses from Gemini.
Includes resilient educational fallback if API key access is restricted.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)


def get_client() -> genai.Client:
    """Initialize and return the Google GenAI Client with validation."""
    load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key in ("YOUR_GEMINI_API_KEY", "your_gemini_api_key_here"):
        raise ValueError(
            "Gemini API key is not configured. Please add your valid GEMINI_API_KEY to the .env file."
        )
    return genai.Client(api_key=api_key)


def get_model() -> str:
    """Retrieve the configured Gemini model name from environment or use default."""
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()


def clean_markdown_json(raw_text: str) -> str:
    """Remove markdown code fences or surrounding text to isolate JSON string."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        return match.group(0)

    array_match = re.search(r"\[[\s\S]*\]", cleaned)
    if array_match:
        return array_match.group(0)

    return cleaned


def validate_and_normalize_quiz(data: Any) -> List[Dict[str, Any]]:
    """Validate and normalize parsed quiz structure to 3 questions, 4 options, 0-based answer."""
    if isinstance(data, dict):
        raw_questions = data.get("questions", [])
    elif isinstance(data, list):
        raw_questions = data
    else:
        raise ValueError("Invalid quiz structure: Expected a JSON object with 'questions' list.")

    if not isinstance(raw_questions, list) or len(raw_questions) == 0:
        raise ValueError("No questions found in generated quiz data.")

    selected_questions = raw_questions[:3]
    normalized_questions: List[Dict[str, Any]] = []

    for idx, item in enumerate(selected_questions, start=1):
        if not isinstance(item, dict):
            continue

        question_text = str(item.get("question", "")).strip()
        if not question_text:
            question_text = f"Question {idx}"

        raw_options = item.get("options", [])
        if not isinstance(raw_options, list):
            raw_options = ["Option A", "Option B", "Option C", "Option D"]

        options = [str(opt).strip() for opt in raw_options][:4]
        while len(options) < 4:
            options.append(f"Option {chr(65 + len(options))}")

        raw_answer = item.get("answer", 0)
        if isinstance(raw_answer, str):
            clean_ans = raw_answer.strip().upper()
            if clean_ans in ("A", "0"):
                answer_idx = 0
            elif clean_ans in ("B", "1"):
                answer_idx = 1
            elif clean_ans in ("C", "2"):
                answer_idx = 2
            elif clean_ans in ("D", "3"):
                answer_idx = 3
            elif clean_ans.isdigit():
                answer_idx = int(clean_ans)
            else:
                answer_idx = 0
        elif isinstance(raw_answer, (int, float)):
            answer_idx = int(raw_answer)
        else:
            answer_idx = 0

        if answer_idx < 0 or answer_idx >= len(options):
            answer_idx = 0

        normalized_questions.append({
            "question": question_text,
            "options": options,
            "answer": answer_idx,
        })

    return normalized_questions


def fallback_quiz(topic_or_text: str) -> List[Dict[str, Any]]:
    """Provide a reliable 3-question MCQ quiz when Gemini API is restricted."""
    t_lower = topic_or_text.lower().strip()

    if "python" in t_lower:
        return [
            {
                "question": "Which keyword is used to define a function in Python?",
                "options": ["func", "def", "function", "define"],
                "answer": 1,
            },
            {
                "question": "Which built-in Python data type is ordered, mutable, and written with square brackets []?",
                "options": ["List", "Tuple", "Dictionary", "Set"],
                "answer": 0,
            },
            {
                "question": "What is the output of len('EduGenie') in Python?",
                "options": ["6", "7", "8", "9"],
                "answer": 2,
            },
        ]
    elif "solar" in t_lower or "planet" in t_lower or "space" in t_lower:
        return [
            {
                "question": "Which planet is known as the 'Red Planet'?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "answer": 1,
            },
            {
                "question": "Which is the largest planet in our solar system?",
                "options": ["Earth", "Saturn", "Jupiter", "Neptune"],
                "answer": 2,
            },
            {
                "question": "What celestial body is at the center of our solar system?",
                "options": ["The Sun", "The Moon", "Jupiter", "Polaris"],
                "answer": 0,
            },
        ]
    elif "sql" in t_lower or "database" in t_lower:
        return [
            {
                "question": "Which SQL statement is used to retrieve data from a database?",
                "options": ["GET", "EXTRACT", "SELECT", "FETCH"],
                "answer": 2,
            },
            {
                "question": "Which SQL clause is used to filter records that meet a specific condition?",
                "options": ["ORDER BY", "WHERE", "GROUP BY", "HAVING"],
                "answer": 1,
            },
            {
                "question": "Which SQL constraint uniquely identifies each record in a database table?",
                "options": ["PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "NOT NULL"],
                "answer": 0,
            },
        ]
    else:
        topic_clean = topic_or_text.strip().title()
        return [
            {
                "question": f"What is the primary objective of studying {topic_clean}?",
                "options": [
                    "To memorize facts without understanding principles",
                    f"To understand foundational concepts and practical applications of {topic_clean}",
                    "To replace all other subjects",
                    "To perform only theoretical mathematical calculations",
                ],
                "answer": 1,
            },
            {
                "question": f"Which of the following is considered best practice when learning {topic_clean}?",
                "options": [
                    "Hands-on practice combined with conceptual review",
                    "Studying only once before an exam",
                    "Skipping the beginner fundamentals",
                    "Ignoring practical real-world examples",
                ],
                "answer": 0,
            },
            {
                "question": f"How can a student effectively measure their progress in {topic_clean}?",
                "options": [
                    "By avoiding tests and quizzes",
                    "By solving practical problems and taking quizzes",
                    "By reading passively without taking notes",
                    "By guessing answers randomly",
                ],
                "answer": 1,
            },
        ]


def generate_quiz(topic_or_text: str) -> List[Dict[str, Any]]:
    """
    Generate exactly 3 multiple-choice questions from a topic or text snippet.

    Args:
        topic_or_text: The subject matter or reading passage.

    Returns:
        A list of 3 normalized question dicts.
    """
    if not topic_or_text or not topic_or_text.strip():
        raise ValueError("Topic or text cannot be empty. Please enter a topic or text for the quiz.")

    prompt = (
        "You are EduGenie, an educational quiz generator for students.\n"
        "Generate a 3-question multiple-choice quiz based on the following topic or passage.\n\n"
        f"Topic/Text:\n{topic_or_text.strip()}\n\n"
        "Requirements:\n"
        "1. Generate EXACTLY 3 questions.\n"
        "2. Each question MUST have EXACTLY 4 options.\n"
        "3. Provide exactly 1 correct answer as a zero-based integer index (0 for first option, 1 for second, 2 for third, 3 for fourth).\n"
        "4. Return ONLY valid JSON adhering strictly to this format:\n"
        "{\n"
        '  "questions": [\n'
        "    {\n"
        '      "question": "Question text here?",\n'
        '      "options": [\n'
        '        "Option A",\n'
        '        "Option B",\n'
        '        "Option C",\n'
        '        "Option D"\n'
        "      ],\n"
        '      "answer": 0\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    try:
        client = get_client()
        model_name = get_model()
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        )
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )

        if not response or not response.text:
            return fallback_quiz(topic_or_text)

        cleaned_json = clean_markdown_json(response.text)
        parsed_data = json.loads(cleaned_json)
        validated = validate_and_normalize_quiz(parsed_data)
        if len(validated) == 3:
            return validated
        return fallback_quiz(topic_or_text)

    except Exception as e:
        err_msg = str(e).lower()
        if (
            "permission_denied" in err_msg
            or "denied access" in err_msg
            or "403" in err_msg
            or "not_found" in err_msg
            or "api_key" in err_msg
            or "resource_exhausted" in err_msg
        ):
            return fallback_quiz(topic_or_text)
        if isinstance(e, ValueError):
            raise
        return fallback_quiz(topic_or_text)

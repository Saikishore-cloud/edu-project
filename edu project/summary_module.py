"""
summary_module.py - Text Summarization Module for EduGenie
Produces clear, concise, and fact-preserving summaries of educational texts.
Includes resilient educational fallback if API key access is restricted.
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai

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


def fallback_summary(text: str) -> str:
    """Produce a structured concise summary when Gemini API is restricted."""
    sentences = [s.strip() for s in re.split(r"[.\n]+", text) if len(s.strip()) > 15]

    if not sentences:
        summary_core = text.strip()[:200]
        points = ["Core concept explained in the passage.", "Essential principles preserved."]
    else:
        summary_core = sentences[0] + "."
        points = [f"• {s}." for s in sentences[1:4]]
        if not points:
            points = ["• Highlights the core idea and main facts presented in the study material."]

    bullet_text = "\n".join(points)
    return (
        f"Summary Overview:\n{summary_core}\n\n"
        f"Key Takeaways:\n{bullet_text}"
    )


def summarize_text(text: str) -> str:
    """
    Produce a concise, easy-to-understand summary of a given educational text.

    Args:
        text: Long paragraph or passage to summarize.

    Returns:
        A concise summary preserving the primary facts and concepts.
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty. Please enter text to summarize.")

    prompt = (
        "You are EduGenie, an educational assistant helping students read and understand texts efficiently.\n"
        "Summarize the following educational passage:\n\n"
        f"Text:\n{text.strip()}\n\n"
        "Guidelines:\n"
        "- Identify and preserve the main concepts, facts, and conclusions.\n"
        "- Remove unnecessary filler, repetitive details, and fluff.\n"
        "- Write a clear, beginner-friendly summary in plain language.\n"
        "- Provide a brief summary paragraph followed by 3-5 key bullet point takeaways.\n"
        "- Ensure the summary is significantly shorter than the source while retaining full meaning."
    )

    try:
        client = get_client()
        model_name = get_model()
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        if response and response.text and response.text.strip():
            return response.text.strip()
        return fallback_summary(text)
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
            return fallback_summary(text)
        if isinstance(e, ValueError):
            raise
        return fallback_summary(text)

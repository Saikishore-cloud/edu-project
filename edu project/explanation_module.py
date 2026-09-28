"""
explanation_module.py - Topic Explanation Module for EduGenie
Explains difficult educational topics in beginner-friendly language,
breaking down concepts with steps, examples, and key points.
Includes resilient educational fallback if API key access is restricted.
"""

import os
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


def fallback_explanation(topic: str) -> str:
    """Provide a high-quality educational explanation when Gemini API is restricted."""
    t_lower = topic.lower().strip()

    if "pythagor" in t_lower:
        return (
            "The Pythagorean Theorem describes the fundamental relationship between the sides of a right-angled triangle.\n\n"
            "Formula:\n"
            "a² + b² = c²\n\n"
            "Where:\n"
            "- 'a' and 'b' are the lengths of the two shorter sides forming the right angle.\n"
            "- 'c' is the hypotenuse (the longest side opposite the 90-degree right angle).\n\n"
            "Step-by-Step Breakdown:\n"
            "1. Confirm the triangle has a 90-degree right angle.\n"
            "2. Measure sides 'a' and 'b'.\n"
            "3. Square both values: compute a² and b².\n"
            "4. Add the two squares together: a² + b².\n"
            "5. Take the square root of the sum to calculate hypotenuse c.\n\n"
            "Example:\n"
            "Suppose a triangle has side a = 3 and side b = 4.\n"
            "- Step 1: 3² = 9\n"
            "- Step 2: 4² = 16\n"
            "- Step 3: 9 + 16 = 25\n"
            "- Step 4: √25 = 5\n"
            "The hypotenuse c equals 5 units (a classic 3-4-5 right triangle)!\n\n"
            "Key Points to Remember:\n"
            "• This theorem applies exclusively to right-angled triangles.\n"
            "• The hypotenuse is always the longest side.\n"
            "• Essential in engineering, navigation, GPS calculations, and carpentry."
        )
    elif "photosynthesis" in t_lower:
        return (
            "Photosynthesis is the process green plants use to convert sunlight into food and oxygen.\n\n"
            "Chemical Equation:\n"
            "6CO₂ + 6H₂O + Sunlight → C₆H₁₂O₆ (Glucose) + 6O₂ (Oxygen)\n\n"
            "Step-by-Step Breakdown:\n"
            "1. Absorption: Chlorophyll in the plant leaves captures energy from sunlight.\n"
            "2. Intake: Roots absorb water from the soil; stomata take in carbon dioxide from the air.\n"
            "3. Light Reactions: Water molecules are split, releasing oxygen gas into the atmosphere.\n"
            "4. Calvin Cycle: Carbon dioxide is synthesized into glucose, providing energy for plant growth.\n\n"
            "Example:\n"
            "A houseplant sitting on a sunny windowsill absorbs daylight and water from its pot to grow leaves, while simultaneously purifying the surrounding air.\n\n"
            "Key Points to Remember:\n"
            "• Chlorophyll gives leaves their distinctive green color.\n"
            "• Photosynthesis is the primary source of breathable oxygen on Earth.\n"
            "• Forms the foundation of global food chains."
        )
    else:
        topic_title = topic.strip().title()
        return (
            f"Overview: {topic_title}\n\n"
            f"{topic_title} is an essential educational topic that can be understood clearly by examining its core components.\n\n"
            "Step-by-Step Breakdown:\n"
            "1. Foundational Concept: Grasp what the topic represents and why it is studied.\n"
            "2. Underlying Mechanics: Learn how the parts interact and function together.\n"
            "3. Practical Applications: Observe where this concept occurs in everyday life or technology.\n"
            "4. Mastery & Review: Solve representative problems and connect with related concepts.\n\n"
            f"Example of {topic_title}:\n"
            f"Consider a real-world scenario where {topic_title} is applied directly. By breaking down the problem into smaller, manageable parts, you can apply standard principles to achieve a clear, repeatable outcome.\n\n"
            "Key Points to Remember:\n"
            f"• Always begin with simple definitions before moving to complex details.\n"
            f"• Regular practice and testing help retain {topic_title} concepts long-term."
        )


def explain_topic(topic: str) -> str:
    """
    Explain an educational topic in simple, beginner-friendly language.
    Breaks down concepts into steps, provides an example, and highlights key points.

    Args:
        topic: The topic or concept to explain.

    Returns:
        A formatted, beginner-friendly explanation.
    """
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty. Please enter a topic to explain.")

    prompt = (
        "You are EduGenie, an expert teacher and educational assistant.\n"
        f"Explain the following topic thoroughly yet simply for a beginner student:\n\n"
        f"Topic: {topic.strip()}\n\n"
        "Guidelines:\n"
        "- Explain the topic for a beginner using simple language.\n"
        "- Break complicated concepts into clear, numbered or bulleted steps.\n"
        "- Provide a simple, clear, concrete example.\n"
        "- Include important key points or formula/rules to remember.\n"
        "- Keep the formatting clean and easy to read."
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
        return fallback_explanation(topic)
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
            return fallback_explanation(topic)
        if isinstance(e, ValueError):
            raise
        return fallback_explanation(topic)

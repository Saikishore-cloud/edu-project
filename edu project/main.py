"""
main.py - FastAPI Application for EduGenie
Google Gemini Powered Learning Assistant
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# Import EduGenie feature modules
from qna import answer_question
from explanation_module import explain_topic
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Initialize FastAPI App
app = FastAPI(
    title="EduGenie",
    description="Google Gemini Powered Learning Assistant for Students",
    version="1.0.0",
)

# Ensure templates and static directories exist
(BASE_DIR / "templates").mkdir(exist_ok=True)
(BASE_DIR / "static").mkdir(exist_ok=True)

# Mount Static Files and Jinja2 Templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class UserInputRequest(BaseModel):
    """Pydantic model for standard user input across all feature endpoints."""
    input: str = Field(..., description="User input text, question, or topic")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors cleanly with standard JSON structure."""
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "Input is required. Please enter a valid text, question, or topic.",
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global fallback exception handler to shield internal details and return clean JSON."""
    error_msg = str(exc)
    # Sanitize any accidental API key leaks in error strings
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key and gemini_key in error_msg:
        error_msg = error_msg.replace(gemini_key, "[REDACTED_API_KEY]")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": error_msg or "An unexpected server error occurred.",
        },
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render and serve the EduGenie single-page web interface."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/qa")
async def endpoint_qa(payload: UserInputRequest):
    """Handle student Q&A requests."""
    user_input = payload.input.strip()
    if not user_input:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Question cannot be empty. Please enter your question."},
        )

    try:
        answer = answer_question(user_input)
        return {"success": True, "result": answer}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"success": False, "error": str(ve)})
    except RuntimeError as re:
        return JSONResponse(status_code=500, content={"success": False, "error": str(re)})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred while answering: {str(e)}"},
        )


@app.post("/explain")
async def endpoint_explain(payload: UserInputRequest):
    """Handle topic explanation requests."""
    user_input = payload.input.strip()
    if not user_input:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Topic cannot be empty. Please enter a topic to explain."},
        )

    try:
        explanation = explain_topic(user_input)
        return {"success": True, "result": explanation}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"success": False, "error": str(ve)})
    except RuntimeError as re:
        return JSONResponse(status_code=500, content={"success": False, "error": str(re)})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred while explaining topic: {str(e)}"},
        )


@app.post("/quiz")
async def endpoint_quiz(payload: UserInputRequest):
    """Handle 3-question MCQ quiz generation requests."""
    user_input = payload.input.strip()
    if not user_input:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Topic or text cannot be empty. Please enter content for the quiz."},
        )

    try:
        questions = generate_quiz(user_input)
        return {"success": True, "questions": questions}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"success": False, "error": str(ve)})
    except RuntimeError as re:
        return JSONResponse(status_code=500, content={"success": False, "error": str(re)})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred while generating quiz: {str(e)}"},
        )


@app.post("/summarize")
async def endpoint_summarize(payload: UserInputRequest):
    """Handle educational text summarization requests."""
    user_input = payload.input.strip()
    if not user_input:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Text cannot be empty. Please enter text to summarize."},
        )

    try:
        summary = summarize_text(user_input)
        return {"success": True, "result": summary}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"success": False, "error": str(ve)})
    except RuntimeError as re:
        return JSONResponse(status_code=500, content={"success": False, "error": str(re)})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred while summarizing text: {str(e)}"},
        )


@app.post("/learn/recommendations")
async def endpoint_learning_recommendations(payload: UserInputRequest):
    """Handle structured learning path generation requests."""
    user_input = payload.input.strip()
    if not user_input:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Topic cannot be empty. Please enter a topic for the learning path."},
        )

    try:
        recommendations = get_learning_recommendations(user_input)
        return {"success": True, "result": recommendations}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"success": False, "error": str(ve)})
    except RuntimeError as re:
        return JSONResponse(status_code=500, content={"success": False, "error": str(re)})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred while generating learning path: {str(e)}"},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

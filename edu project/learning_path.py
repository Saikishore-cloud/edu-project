"""
learning_path.py - Learning Path Generator Module for EduGenie
Generates structured roadmaps from Beginner to Advanced with timelines,
practice projects, and learning resources.
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


def fallback_learning_path(topic: str) -> str:
    """Generate a structured learning path when Gemini API is restricted."""
    t_title = topic.strip().title()
    t_lower = topic.lower().strip()

    if "python" in t_lower:
        return (
            "Topic: Python\n\n"
            "Beginner\n"
            "1. Python Syntax & Indentation\n"
            "2. Variables, Dynamic Typing & Expressions\n"
            "3. Core Data Types (integers, floats, strings, booleans)\n"
            "4. Basic Operators & String Manipulation\n"
            "5. Conditional Logic (if, elif, else)\n"
            "6. Loops (for, while, range, break, continue)\n"
            "7. Functions, Parameters & Return Values\n"
            "8. Lists, Tuples, Dictionaries & Sets\n\n"
            "Intermediate\n"
            "1. Object-Oriented Programming (Classes, Inheritance, Polymorphism)\n"
            "2. Modular Code & Package Imports\n"
            "3. Exception & Error Handling (try, except, finally)\n"
            "4. File I/O (JSON, CSV, Text)\n"
            "5. List Comprehensions & Lambda Functions\n"
            "6. Consuming REST APIs with Requests / HTTPX\n"
            "7. Virtual Environments & Pip Package Management\n\n"
            "Advanced\n"
            "1. Asynchronous Programming (asyncio, coroutines)\n"
            "2. Decorators, Generators & Context Managers\n"
            "3. Web Frameworks (FastAPI / Django)\n"
            "4. Unit Testing with Pytest & Test-Driven Development\n"
            "5. Performance Profiling, Memory Optimization & Multiprocessing\n\n"
            "Suggested Timeline\n"
            "- Month 1 → Beginner fundamentals & weekly small scripts\n"
            "- Month 2–3 → Intermediate OOP, API integration & data processing\n"
            "- Month 4–6 → Advanced web services, async workflows & production deployment\n\n"
            "Practice Projects\n"
            "- Beginner: CLI To-Do App, Temperature Converter, Quiz Game\n"
            "- Intermediate: Personal Expense Tracker, Web Scraper, Weather API Dashboard\n"
            "- Advanced: Full-stack REST API with FastAPI, Real-time Chat, AI Assistant Integration\n\n"
            "Recommended Resources\n"
            "- Official Python Documentation (docs.python.org)\n"
            "- 'Automate the Boring Stuff with Python' by Al Sweigart\n"
            "- Real Python (realpython.com)\n\n"
            "Learning Tips\n"
            "• Write code every day for at least 30-45 minutes.\n"
            "• Build projects rather than just passively watching video tutorials.\n"
            "• Use Python's built-in interactive shell (REPL) to test small ideas quickly."
        )
    elif "sql" in t_lower:
        return (
            "Topic: SQL (Structured Query Language)\n\n"
            "Beginner\n"
            "1. Relational Database Concepts & Tables\n"
            "2. SELECT, FROM, and Column Aliases\n"
            "3. Filtering Rows with WHERE, AND, OR, NOT\n"
            "4. Sorting Data with ORDER BY & Limiting Rows (LIMIT / TOP)\n"
            "5. Aggregate Functions (COUNT, SUM, AVG, MIN, MAX)\n"
            "6. GROUP BY & HAVING Clauses\n"
            "7. Basic Table Joins (INNER JOIN)\n\n"
            "Intermediate\n"
            "1. Advanced Joins (LEFT, RIGHT, FULL OUTER, CROSS JOIN)\n"
            "2. Subqueries & Nested Queries\n"
            "3. Common Table Expressions (WITH / CTEs)\n"
            "4. Primary Keys, Foreign Keys & Table Constraints\n"
            "5. Data Modification (INSERT, UPDATE, DELETE, UPSERT)\n"
            "6. Window Functions (ROW_NUMBER, RANK, DENSE_RANK, PARTITION BY)\n\n"
            "Advanced\n"
            "1. Database Indexing (B-Tree, Hash, Clustered vs Non-Clustered)\n"
            "2. Query Execution Plans & Performance Optimization (EXPLAIN ANALYZE)\n"
            "3. Transactions & ACID Compliance (BEGIN, COMMIT, ROLLBACK)\n"
            "4. Stored Procedures, Triggers & User-Defined Functions\n"
            "5. Database Normalization (1NF to 3NF) & Schema Design\n\n"
            "Suggested Timeline\n"
            "- Month 1 → Beginner query foundations & relational modeling\n"
            "- Month 2–3 → Intermediate joins, aggregations, CTEs & window analytics\n"
            "- Month 4–6 → Advanced query optimization, indexing & database administration\n\n"
            "Practice Projects\n"
            "- Beginner: Library Book Tracking Database\n"
            "- Intermediate: E-Commerce Sales & Analytics Report Generator\n"
            "- Advanced: Database Migration, Index Tuning & High-Throughput Inventory System\n\n"
            "Recommended Resources\n"
            "- Mode Analytics SQL Tutorial (mode.com/sql-tutorial)\n"
            "- PostgreSQL Official Documentation\n"
            "- LeetCode & HackerRank Database Practice Tracks\n\n"
            "Learning Tips\n"
            "• Practice formatting queries with indentation for readable SQL.\n"
            "• Always test queries with SELECT before running destructive UPDATE or DELETE statements."
        )
    else:
        return (
            f"Topic: {t_title}\n\n"
            "Beginner\n"
            f"1. Fundamental Concepts & Terminology of {t_title}\n"
            "2. Core Principles, Purpose & Scope\n"
            "3. Development Environment Setup & Essential Tools\n"
            "4. Basic Syntax, Rules, or Standards\n"
            "5. Foundational Workflows & First Practice Exercises\n"
            "6. Common Beginner Mistakes & How to Avoid Them\n\n"
            "Intermediate\n"
            f"1. Practical Modular Techniques in {t_title}\n"
            "2. Integration with Complementary Technologies & Frameworks\n"
            "3. Data Handling, Structuring & Validation\n"
            "4. Debugging, Troubleshooting & Diagnostics\n"
            "5. Intermediate Project Architecture\n\n"
            "Advanced\n"
            f"1. High-Performance Optimization & Scalability in {t_title}\n"
            "2. Architectural Patterns & Clean Design\n"
            "3. Security Hardening & Best Practices\n"
            "4. Automated Testing, CI/CD & Production Deployment\n"
            "5. Advanced Real-World Problem Solving\n\n"
            "Suggested Timeline\n"
            "- Month 1 → Beginner core foundations & fundamentals\n"
            "- Month 2–3 → Intermediate projects & tool mastery\n"
            "- Month 4–6 → Advanced specialization & production portfolio\n\n"
            "Practice Projects\n"
            f"- Beginner: Introductory Hands-on Exercise in {t_title}\n"
            f"- Intermediate: End-to-End Application utilizing {t_title}\n"
            f"- Advanced: Production-Ready, Optimized System\n\n"
            "Recommended Resources\n"
            f"- Official {t_title} Documentation & Standards Guide\n"
            "- Community Open-Source Repositories on GitHub\n"
            "- Interactive Learning Platforms & Practice Katas\n\n"
            "Learning Tips\n"
            "• Consistency is key: dedicate time daily rather than cramming weekly.\n"
            "• Build hands-on projects to anchor theoretical knowledge."
        )


def get_learning_recommendations(topic: str) -> str:
    """
    Generate a complete, structured learning path for a given topic or technology.

    Args:
        topic: The subject to learn (e.g. 'Python', 'SQL', 'Machine Learning').

    Returns:
        A formatted roadmap containing Beginner, Intermediate, Advanced stages,
        timeline, practice projects, and resources.
    """
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty. Please enter a topic for the learning path.")

    prompt = (
        "You are EduGenie, an expert curriculum designer and educational mentor.\n"
        f"Generate a clear, well-structured learning path for the following subject:\n\n"
        f"Topic: {topic.strip()}\n\n"
        "Structure the learning path with the following exact sections:\n"
        f"Topic: {topic.strip()}\n\n"
        "Beginner\n"
        "Numbered list of 5-8 foundational topics/concepts to learn.\n\n"
        "Intermediate\n"
        "Numbered list of 5-8 intermediate concepts, techniques, and tools.\n\n"
        "Advanced\n"
        "Numbered list of 5-8 advanced topics, architecture, and optimizations.\n\n"
        "Suggested Timeline\n"
        "- Month 1 → Beginner foundations\n"
        "- Month 2–3 → Intermediate mastery\n"
        "- Month 4–6 → Advanced specialization\n\n"
        "Practice Projects\n"
        "- Beginner: [1-2 project ideas]\n"
        "- Intermediate: [1-2 project ideas]\n"
        "- Advanced: [1-2 project ideas]\n\n"
        "Recommended Resources\n"
        "- High-quality free documentation, books, or platforms.\n\n"
        "Learning Tips\n"
        "- 3-4 actionable tips for consistency and hands-on practice.\n\n"
        "Ensure the format is clean, easy to read, and motivating for students."
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
        return fallback_learning_path(topic)
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
            return fallback_learning_path(topic)
        if isinstance(e, ValueError):
            raise
        return fallback_learning_path(topic)

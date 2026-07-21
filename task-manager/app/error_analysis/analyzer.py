import json

from google import genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.models import ErrorLog

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are a senior Python backend engineer.

Analyze the given application error.

Return ONLY valid JSON in this exact format:

{
    "root_cause": "...",
    "suggested_fix": "..."
}

Do not include markdown.
Do not wrap the JSON inside ``` blocks.
Do not provide any explanation.
Return only the JSON object.
"""


async def analyze_error(error: ErrorLog) -> dict:
    user_prompt = f"""
Endpoint:
{error.endpoint}

HTTP Method:
{error.http_method}

Exception Type:
{error.exception_type}

Error Message:
{error.error_message}

Stack Trace:
{error.stack_trace}
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                SYSTEM_PROMPT,
                user_prompt,
            ],
        )

    except Exception as e:
        raise Exception(f"Gemini API error: {e}")

    result = json.loads(response.text)

    return {
        "root_cause": result["root_cause"],
        "suggested_fix": result["suggested_fix"],
        "llm_model": GEMINI_MODEL,
    }

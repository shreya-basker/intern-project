from google.genai import types
from pydantic import ValidationError

from app.ai.client import client
from app.ai.prompt import SYSTEM_PROMPT, build_prompt
from app.ai.schemas import AIAnalysis
from app.config import GEMINI_MODEL
from app.error_analysis.sanitizer import sanitize_text


def shorten_traceback(traceback: str) -> str:
    if not traceback:
        return ""

    lines = traceback.strip().splitlines()

    result = []

    for i, line in enumerate(lines):
        if line.lstrip().startswith("File ") and "/app/" in line:
            result.append(line)

            # Include the following source code line if present
            if i + 1 < len(lines):
                result.append(lines[i + 1])

    # Always include the exception message
    if lines:
        result.append(lines[-1])

    return "\n".join(result)


class AIAnalysisError(Exception):
    """Raised when AI analysis cannot be completed."""


class GeminiService:
    """Service responsible for generating AI analysis for application errors."""

    MODEL = GEMINI_MODEL

    def analyze(self, error) -> AIAnalysis:
        """
        Analyze an ErrorLog instance using Gemini.

        Args:
            error: ErrorLog ORM object

        Returns:
            AIAnalysis

        Raises:
            AIAnalysisError
        """

        prompt = self._build_prompt(error)

        response = self._generate(prompt)

        return self._parse(response)

    def _build_prompt(self, error) -> str:
        print(shorten_traceback(error.stack_trace))
        safe_message = sanitize_text(error.error_message or "")
        safe_traceback = sanitize_text(shorten_traceback(error.stack_trace or ""))

        return build_prompt(
            endpoint=error.endpoint,
            http_method=error.http_method,
            exception_type=error.exception_type,
            exception_message=safe_message,
            traceback=safe_traceback,
        )

    def _generate(self, prompt: str):
        """
        Sends the prompt to Gemini.
        """

        try:
            response = client.models.generate_content(
                model=self.MODEL,
                contents=[
                    SYSTEM_PROMPT,
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )

            if not response.text:
                raise AIAnalysisError("Gemini returned an empty response.")

            return response

        except Exception as exc:
            raise AIAnalysisError(f"Failed to generate AI analysis: {exc}") from exc

    def _parse(self, response) -> AIAnalysis:
        """
        Validates Gemini's JSON response.
        """

        try:
            return AIAnalysis.model_validate_json(response.text)

        except ValidationError as exc:
            raise AIAnalysisError(f"Gemini returned invalid JSON:\n{response.text}") from exc

from app.error_analysis.config import SanitizeConfig
from app.error_analysis.entropy import redact_high_entropy_strings
from app.error_analysis.redactor import redact_known_patterns

config = SanitizeConfig()


def sanitize_text(text: str) -> str:
    if not text:
        return text

    cleaned = text
    cleaned = redact_known_patterns(cleaned)

    if config.detect_high_entropy:
        cleaned = redact_high_entropy_strings(
            cleaned, threshold=config.entropy_threshold, minimum_length=config.minimum_secret_length
        )
    return cleaned

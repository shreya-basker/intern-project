import re

PATTERNS = [
    (
        re.compile(
            r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
            re.IGNORECASE,
        ),
        "Bearer <REDACTED>",
    ),
    (
        re.compile(
            r"(Authorization:\s*)(.+)",
            re.IGNORECASE,
        ),
        r"\1<REDACTED>",
    ),
    (
        re.compile(
            r"(password|passwd|secret|api[_-]?key)\s*=\s*([^\s]+)",
            re.IGNORECASE,
        ),
        r"\1=<REDACTED>",
    ),
    (
        re.compile(
            r"(postgres(?:ql)?://)([^:@]+):([^@]+)@",
            re.IGNORECASE,
        ),
        r"\1<REDACTED>@",
    ),
]


def redact_known_patterns(text: str):
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)

    return text

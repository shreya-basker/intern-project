import math
import re
from collections import Counter

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_\-+/=]{20,}")


def shannon_entropy(text: str) -> float:
    if not text:
        return 0
    counts = Counter(text)
    length = len(text)

    entropy = 0.0

    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    return entropy


def redact_high_entropy_strings(text: str, threshold: float, minimum_length: int):
    def replace(match):
        token = match.group()

        if len(token) < minimum_length:
            return token
        if shannon_entropy(text) >= threshold:
            return "<HIGH_ENTROPY_SECRET>"

        return token

    return TOKEN_PATTERN.sub(replace, text)

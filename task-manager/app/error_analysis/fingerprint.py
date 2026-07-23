import hashlib


def generate_fingerprint(exception_type: str, endpoint: str, message: str) -> str:
    data = f"{exception_type} | {endpoint} | {message}"
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

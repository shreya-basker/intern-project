from app.error_analysis.sanitizer import sanitize_text


def test_redacts_bearer_token():
    text = "Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456"

    cleaned = sanitize_text(text)

    assert "<REDACTED>" in cleaned
    assert "abcdefghijklmnopqrstuvwxyz123456" not in cleaned


def test_redacts_password():
    text = "password=mySuperSecretPassword"

    cleaned = sanitize_text(text)

    assert "password=<REDACTED>" == cleaned


def test_redacts_api_key():
    text = "api_key=sk-test-123456789"

    cleaned = sanitize_text(text)

    assert "api_key=<REDACTED>" == cleaned


def test_redacts_high_entropy_string():
    secret = "AJDKLQWIEURYZXCMNB1234567890QWERTY"

    cleaned = sanitize_text(secret)

    assert "<HIGH_ENTROPY_SECRET>" == cleaned


def test_normal_text_not_modified():
    text = "ValueError: User not found"

    cleaned = sanitize_text(text)

    assert cleaned == text


def test_sentence_not_redacted():
    text = "This exception occurred while processing the user registration request."

    cleaned = sanitize_text(text)

    assert cleaned == text


def test_database_url_redacted():
    text = "postgresql://admin:SuperSecretPassword@localhost/app_db"

    cleaned = sanitize_text(text)

    assert "SuperSecretPassword" not in cleaned


def test_multiple_secrets():
    text = """
Authorization: Bearer abcdefghijklmnopqrstuvwxyz

password=myPassword

api_key=sk-123456789
"""

    cleaned = sanitize_text(text)

    assert "myPassword" not in cleaned
    assert "sk-123456789" not in cleaned
    assert "Bearer abcdef" not in cleaned

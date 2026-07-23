from dataclasses import dataclass


@dataclass(slots=True)
class SanitizeConfig:
    redact_api_keys: bool = True
    redact_tokens: bool = True
    redact_passwords: bool = True
    redact_connection_strings: bool = True
    redact_emails: bool = False
    redact_ip_addresses: bool = False

    detect_high_entropy: bool = True
    entropy_threshold: float = 4.0
    minimum_secret_length: int = 20

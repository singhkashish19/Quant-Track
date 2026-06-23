import os
import time


def setup_module(module):
    # Ensure SECRET_KEY is set before importing modules that load settings
    os.environ.setdefault("SECRET_KEY", "test_secret_key_at_least_32_characters_long_1234")


def test_password_hash_and_verify():
    from app.auth.security import hash_password, verify_password

    pw = "S3cureP@ssw0rd!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)


def test_token_create_and_verify():
    from app.auth.security import create_access_token, verify_token

    token = create_access_token(subject=123)
    assert token and isinstance(token, str)

    payload = verify_token(token)
    assert payload is not None
    assert payload.get("sub") == "123"
    assert payload.get("type") == "access"


def test_refresh_token_flow():
    from app.auth.security import create_refresh_token, verify_token

    rt = create_refresh_token(subject=42)
    payload = verify_token(rt)
    assert payload is not None
    assert payload.get("sub") == "42"
    assert payload.get("type") == "refresh"

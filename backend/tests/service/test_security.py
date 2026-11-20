"""
Tests for password hashing and login tokens (app/core/security.py).
"""


import jwt

from app.core import config
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# ============================================================
# Passwords
# ============================================================

def test_hash_is_not_the_plain_password():
    hashed = hash_password("Password123")

    assert hashed != "Password123"
    assert "Password123" not in hashed


def test_correct_password_verifies():
    assert verify_password("Password123", hash_password("Password123"))


def test_wrong_password_does_not_verify():
    assert not verify_password("password123", hash_password("Password123"))


def test_same_password_gets_a_different_hash_each_time():
    """Each hash has its own random salt."""
    assert hash_password("Password123") != hash_password("Password123")


def test_malformed_stored_hash_does_not_verify_or_crash():
    assert verify_password("Password123", "not-a-bcrypt-hash") is False


# ============================================================
# Tokens
# ============================================================

def test_token_round_trip_returns_the_user_id():
    token = create_access_token("customer-1", "customer")

    assert decode_access_token(token) == "customer-1"


def test_tampered_token_is_rejected():
    token = create_access_token("customer-1", "customer")

    assert decode_access_token(token + "x") is None


def test_garbage_is_rejected():
    assert decode_access_token("garbage") is None
    assert decode_access_token("") is None


def test_expired_token_is_rejected(monkeypatch):
    monkeypatch.setattr(config, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)
    token = create_access_token("customer-1", "customer")

    assert decode_access_token(token) is None


def test_token_without_a_user_id_is_rejected():
    token = jwt.encode(
        {"role": "customer"},
        config.JWT_SECRET,
        algorithm=config.JWT_ALGORITHM,
    )

    assert decode_access_token(token) is None

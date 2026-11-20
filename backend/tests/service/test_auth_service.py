"""
Tests for the auth service (login and token-to-user).
"""


import pytest
from fastapi import HTTPException

from app.core.security import create_access_token
from app.services.auth_service import get_user_from_token, login


@pytest.fixture
def path(customers_file):
    return customers_file


def test_login_returns_a_token_that_identifies_the_user(path, add_account):
    add_account("c1", email="ana@example.com")

    token = login("ana@example.com", "Password123", path).access_token

    assert get_user_from_token(token, path)["id"] == "c1"


def test_wrong_password_is_401(path, add_account):
    add_account("c1", email="ana@example.com")

    with pytest.raises(HTTPException) as error:
        login("ana@example.com", "WrongPassword", path)

    assert error.value.status_code == 401


def test_unknown_email_gives_the_same_401_and_message(path, add_account):
    add_account("c1", email="ana@example.com")

    with pytest.raises(HTTPException) as wrong_password:
        login("ana@example.com", "WrongPassword", path)

    with pytest.raises(HTTPException) as unknown_email:
        login("nobody@example.com", "Password123", path)

    assert unknown_email.value.status_code == 401
    assert unknown_email.value.detail == wrong_password.value.detail


def test_deactivated_account_with_right_password_is_403(path, add_account):
    add_account("c1", email="ana@example.com", active=False)

    with pytest.raises(HTTPException) as error:
        login("ana@example.com", "Password123", path)

    assert error.value.status_code == 403


def test_deactivated_account_with_wrong_password_is_still_401(
    path,
    add_account,
):
    """Do not reveal that an account is deactivated to a guesser."""
    add_account("c1", email="ana@example.com", active=False)

    with pytest.raises(HTTPException) as error:
        login("ana@example.com", "WrongPassword", path)

    assert error.value.status_code == 401


def test_get_user_from_invalid_token_is_401(path):
    with pytest.raises(HTTPException) as error:
        get_user_from_token("garbage", path)

    assert error.value.status_code == 401


def test_get_user_for_deactivated_account_is_403(path, add_account):
    add_account("c1", active=False)

    with pytest.raises(HTTPException) as error:
        get_user_from_token(create_access_token("c1", "customer"), path)

    assert error.value.status_code == 403

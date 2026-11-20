"""
Repository functions for customer JSON persistence.

The repository reads and writes backend/data/customers.json. It does
no validation, hashing, or HTTP handling; the service layer does that.

Every function takes an optional path so tests can use a temporary
file. When no path is given, the path in app.core.config is used.
It is looked up on each call, so tests can also replace
config.CUSTOMERS_FILE for the whole application.
"""


import json
from pathlib import Path

from app.core import config


def _resolve(path: Path | None) -> Path:
    """Return the given path, or the configured customers file."""
    return path if path is not None else config.CUSTOMERS_FILE


def load_customers(path: Path | None = None) -> list[dict]:
    """
    Load all customer records.

    Returns an empty list if the file does not exist yet, so a fresh
    install can register the first customer.
    """
    file_path = _resolve(path)

    if not file_path.exists():
        return []

    with file_path.open(encoding="utf-8") as file:
        return json.load(file)


def load_customer_by_id(
    customer_id: str,
    path: Path | None = None,
) -> dict | None:
    """Return the customer with this ID, or None if there is none."""
    for customer in load_customers(path):
        if customer["id"] == customer_id:
            return customer

    return None


def load_customer_by_email(
    email: str,
    path: Path | None = None,
) -> dict | None:
    """
    Return the customer with this email, or None if there is none.

    Emails are stored lowercase, so the comparison is case-insensitive.
    """
    wanted = email.strip().lower()

    for customer in load_customers(path):
        if customer["email"] == wanted:
            return customer

    return None


def save_customers(
    customers: list[dict],
    path: Path | None = None,
) -> None:
    """Overwrite the customers file with the given records."""
    file_path = _resolve(path)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(customers, file, indent=2)

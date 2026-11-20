"""
Tests for the customer repository (JSON file storage).
"""


import json

from app.repositories.customer_repository import (
    load_customer_by_email,
    load_customer_by_id,
    load_customers,
    save_customers,
)


SAMPLE = [
    {"id": "c1", "email": "ana@example.com", "name": "Ana"},
    {"id": "c2", "email": "ben@example.com", "name": "Ben"},
]


def test_missing_file_loads_as_empty_list(tmp_path):
    assert load_customers(tmp_path / "nope.json") == []


def test_save_then_load_returns_the_same_records(tmp_path):
    path = tmp_path / "customers.json"

    save_customers(SAMPLE, path)

    assert load_customers(path) == SAMPLE


def test_saved_file_is_valid_json_on_disk(tmp_path):
    """Records survive in the file itself, not just in memory."""
    path = tmp_path / "customers.json"

    save_customers(SAMPLE, path)

    assert json.loads(path.read_text(encoding="utf-8")) == SAMPLE


def test_load_by_id_finds_the_record(tmp_path):
    path = tmp_path / "customers.json"
    save_customers(SAMPLE, path)

    assert load_customer_by_id("c2", path)["name"] == "Ben"


def test_load_by_id_returns_none_when_missing(tmp_path):
    path = tmp_path / "customers.json"
    save_customers(SAMPLE, path)

    assert load_customer_by_id("nobody", path) is None


def test_load_by_email_is_case_insensitive(tmp_path):
    path = tmp_path / "customers.json"
    save_customers(SAMPLE, path)

    assert load_customer_by_email("  ANA@Example.com ", path)["id"] == "c1"


def test_load_by_email_returns_none_when_missing(tmp_path):
    path = tmp_path / "customers.json"
    save_customers(SAMPLE, path)

    assert load_customer_by_email("zed@example.com", path) is None

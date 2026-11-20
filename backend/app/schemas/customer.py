"""
Pydantic schemas for customer accounts.

    Customer:
        What the API returns. It never contains the password hash.

    CustomerCreate:
        Validates registration data.

    CustomerUpdate:
        Validates partial profile updates.

Clients cannot choose their own ID, role, or active status.
Registration always creates an active customer, and CustomerUpdate
rejects any field it does not list.
"""


import re

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# A simple shape check: something@something.something, no spaces.
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(value: str) -> str:
    """
    Trim and lowercase an email, and reject values that are not emails.

    Lowercasing makes "Ana@x.com" and "ana@x.com" the same account.
    """
    email = value.strip().lower()

    if not _EMAIL_PATTERN.match(email):
        raise ValueError("Enter a valid email address")

    return email


# ============================================================
# Customer Returned by the API
# ============================================================

class Customer(BaseModel):
    """A customer or staff account without its password hash."""

    id: str
    name: str
    email: str
    address: str | None = None
    role: str
    active: bool


# ============================================================
# Registration
# ============================================================

class CustomerCreate(BaseModel):
    """
    Validate information submitted when registering.

    password must be 8 to 72 bytes long. bcrypt ignores everything
    after 72 bytes, so longer passwords are rejected instead of
    being silently cut short.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    name: str = Field(min_length=1, max_length=100)
    email: str
    password: str = Field(min_length=8, max_length=72)
    address: str | None = Field(default=None, min_length=1, max_length=200)

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def check_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        return value


# ============================================================
# Profile Update
# ============================================================

class CustomerUpdate(BaseModel):
    """
    Validate a partial profile update.

    Omitted fields are left unchanged. Explicit nulls are rejected.
    Email, role and active status cannot be changed here.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    name: str | None = Field(default=None, min_length=1, max_length=100)
    address: str | None = Field(default=None, min_length=1, max_length=200)

    @model_validator(mode="before")
    @classmethod
    def reject_null_values(cls, data):
        if isinstance(data, dict):
            for field in ("name", "address"):
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null")

        return data

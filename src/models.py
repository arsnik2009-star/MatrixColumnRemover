"""JSON-модели банковского REST API."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


API_VERSION = "1.0"


class AccountCreate(BaseModel):
    owner: str = Field(min_length=2, max_length=80)
    opening_balance: Decimal = Field(default=Decimal("0"), ge=0)

    @field_validator("owner")
    @classmethod
    def owner_must_not_be_blank(cls, value: str) -> str:
        owner = value.strip()
        if not owner:
            raise ValueError("владелец счёта не указан")
        return owner


class AmountRequest(BaseModel):
    amount: Decimal = Field(gt=0)


class TransferRequest(AmountRequest):
    schema_version: str = API_VERSION
    source_account_id: str = Field(min_length=1)
    destination_account_id: str = Field(min_length=1)


class AccountResponse(BaseModel):
    schema_version: str = API_VERSION
    account_id: str
    owner: str
    balance: Decimal


class TransferResponse(BaseModel):
    schema_version: str = API_VERSION
    transaction_id: str
    status: Literal["completed"] = "completed"
    source_account_id: str
    destination_account_id: str
    amount: Decimal
    source_balance: Decimal
    destination_balance: Decimal


class HistoryItem(BaseModel):
    transaction_id: str
    source_account_id: str
    destination_account_id: str
    amount: Decimal
    status: str


class HistoryResponse(BaseModel):
    schema_version: str = API_VERSION
    account_id: str
    operations: list[HistoryItem]

"""Модульные тесты операций со счетами."""

from decimal import Decimal

import pytest

from src.account_service import AccountService
from src.errors import AccountNotFoundError, InsufficientFundsError
from src.models import AccountCreate


@pytest.fixture
def service():
    return AccountService()


def test_create_account(service):
    account = service.create(AccountCreate(owner="Арсений", opening_balance="100.125"))
    assert account.account_id == "ACC-0001"
    assert account.balance == Decimal("100.13")


def test_deposit(service):
    account = service.create(AccountCreate(owner="Арсений"))
    updated = service.deposit(account.account_id, Decimal("55.50"))
    assert updated.balance == Decimal("55.50")


def test_withdraw(service):
    account = service.create(AccountCreate(owner="Арсений", opening_balance="100"))
    updated = service.withdraw(account.account_id, Decimal("25.25"))
    assert updated.balance == Decimal("74.75")


def test_missing_account(service):
    with pytest.raises(AccountNotFoundError):
        service.get("ACC-9999")


def test_insufficient_funds(service):
    account = service.create(AccountCreate(owner="Арсений", opening_balance="10"))
    with pytest.raises(InsufficientFundsError):
        service.withdraw(account.account_id, Decimal("11"))

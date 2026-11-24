"""Причинно-следственная таблица перевода и проверка целостности."""

from decimal import Decimal
from itertools import product

import pytest

from src.account_service import AccountService
from src.errors import (
    AccountNotFoundError,
    InsufficientFundsError,
    IntegrationTimeoutError,
    InvalidIntegrationDataError,
    ModuleUnavailableError,
    VersionConflictError,
)
from src.integration import BankingProcessor
from src.models import AccountCreate, TransferRequest
from src.report_service import ReportService
from src.transaction_service import TransactionService


@pytest.fixture
def services():
    accounts = AccountService()
    reports = ReportService()
    transactions = TransactionService(accounts, reports)
    return accounts, reports, transactions


@pytest.mark.parametrize(
    ("accounts_present", "transactions_present", "reports_present"),
    product((False, True), repeat=3),
)
def test_required_module_combinations(services, accounts_present, transactions_present,
                                      reports_present):
    present = (accounts_present, transactions_present, reports_present)
    arguments = [service if included else None for service, included in zip(services, present)]
    if all(present):
        processor = BankingProcessor(*arguments)
        assert (processor.account_service, processor.transaction_service,
                processor.report_service) == services
    else:
        with pytest.raises(ModuleUnavailableError):
            BankingProcessor(*arguments)


@pytest.mark.parametrize(("version", "timeout", "same", "amount", "error"), [
    ("1.0", 1, False, "0.01", None),
    ("1.0", 1, False, "10.00", None),
    ("1.0", 1, False, "10.01", InsufficientFundsError),
    ("1.0", 1, True, "0.01", InvalidIntegrationDataError),
    ("1.0", 1, True, "10.01", InvalidIntegrationDataError),
    ("1.0", 0, False, "0.01", IntegrationTimeoutError),
    ("1.0", 0, True, "10.01", IntegrationTimeoutError),
    ("2.0", 1, False, "0.01", VersionConflictError),
    ("2.0", 0, True, "10.01", VersionConflictError),
])
def test_transfer_decision_table(services, version, timeout, same, amount, error):
    accounts, reports, transactions = services
    source = accounts.create(AccountCreate(owner="Иван", opening_balance="10")).account_id
    target = accounts.create(AccountCreate(owner="Анна")).account_id
    request = TransferRequest(
        schema_version=version, source_account_id=source,
        destination_account_id=source if same else target, amount=amount,
    )
    processor = BankingProcessor(accounts, transactions, reports)
    if error is None:
        operation = processor.transfer(request, timeout)
        assert operation.source_balance == Decimal("10") - Decimal(amount)
        assert operation.destination_balance == Decimal(amount)
        source_history = reports.history(source).operations
        assert reports.history(target).operations == source_history
        assert [(item.transaction_id, item.amount) for item in source_history] == [
            (operation.transaction_id, Decimal(amount)),
        ]
    else:
        with pytest.raises(error):
            processor.transfer(request, timeout)
        assert accounts.get(source).balance == Decimal("10")
        assert accounts.get(target).balance == Decimal("0")
        assert reports.history(source).operations == []
        assert reports.history(target).operations == []


@pytest.mark.regression
def test_missing_recipient_restores_balance_and_skips_history(services):
    accounts, reports, transactions = services
    source = accounts.create(AccountCreate(owner="Иван", opening_balance="10")).account_id
    request = TransferRequest(source_account_id=source, destination_account_id="X", amount="4")
    with pytest.raises(AccountNotFoundError):
        transactions.transfer(request)
    assert accounts.get(source).balance == Decimal("10")
    assert reports.history(source).operations == []

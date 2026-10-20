"""Интеграционные тесты банковских модулей."""

import time

import pytest

from src.account_service import AccountService
from src.errors import (
    IntegrationTimeoutError,
    InvalidIntegrationDataError,
    ModuleUnavailableError,
    VersionConflictError,
)
from src.integration import BankingProcessor
from src.models import AccountCreate, TransferRequest
from src.report_service import ReportService
from src.stubs import AccountServiceStub, ReportServiceStub, TransactionServiceStub
from src.transaction_service import TransactionService


def request(**changes):
    data = {
        "schema_version": "1.0",
        "source_account_id": "ACC-0001",
        "destination_account_id": "ACC-0002",
        "amount": "100.00",
    }
    data.update(changes)
    return TransferRequest.model_validate(data)


def real_processor():
    accounts = AccountService()
    reports = ReportService()
    transactions = TransactionService(accounts, reports)
    processor = BankingProcessor(accounts, transactions, reports)
    source = accounts.create(AccountCreate(owner="Отправитель", opening_balance="500"))
    destination = accounts.create(AccountCreate(owner="Получатель", opening_balance="50"))
    return processor, source, destination


def test_top_down_stage_works_with_stubs():
    processor = BankingProcessor(
        AccountServiceStub(),
        TransactionServiceStub(),
        ReportServiceStub(),
    )
    result = processor.transfer(request())
    assert result.transaction_id == "TRX-STUB"


def test_real_modules_transfer_money_and_write_history():
    processor, source, destination = real_processor()
    result = processor.transfer(request(
        source_account_id=source.account_id,
        destination_account_id=destination.account_id,
    ))
    assert result.source_balance == 400
    assert result.destination_balance == 150
    assert len(processor.report_service.history(source.account_id).operations) == 1


def test_same_account_is_rejected():
    processor, source, _ = real_processor()
    with pytest.raises(InvalidIntegrationDataError):
        processor.transfer(request(
            source_account_id=source.account_id,
            destination_account_id=source.account_id,
        ))


def test_version_conflict_is_detected():
    processor, _, _ = real_processor()
    with pytest.raises(VersionConflictError):
        processor.transfer(request(schema_version="2.0"))


def test_missing_module_is_detected():
    with pytest.raises(ModuleUnavailableError):
        BankingProcessor(None, TransactionServiceStub(), ReportServiceStub())


def test_unexpected_module_failure_is_wrapped():
    class BrokenTransactions:
        def transfer(self, value):
            raise RuntimeError("сбой")

    processor = BankingProcessor(AccountServiceStub(), BrokenTransactions(), ReportServiceStub())
    with pytest.raises(ModuleUnavailableError):
        processor.transfer(request())


def test_non_positive_timeout_is_rejected():
    processor = BankingProcessor(
        AccountServiceStub(),
        TransactionServiceStub(),
        ReportServiceStub(),
    )
    with pytest.raises(IntegrationTimeoutError):
        processor.transfer(request(), timeout_seconds=0)


def test_slow_module_causes_timeout():
    class SlowTransactions(TransactionServiceStub):
        def transfer(self, value):
            time.sleep(0.05)
            return super().transfer(value)

    processor = BankingProcessor(AccountServiceStub(), SlowTransactions(), ReportServiceStub())
    with pytest.raises(IntegrationTimeoutError):
        processor.transfer(request(), timeout_seconds=0.001)

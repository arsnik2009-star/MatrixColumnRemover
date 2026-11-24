"""Модульные проверки моделей, отчётов, ошибок, заглушек и запуска."""

from decimal import Decimal
import runpy

import pytest
import uvicorn

from src import errors
from src.models import AccountCreate, AmountRequest, HistoryItem
from src.report_service import ReportService
from src.stubs import AccountServiceStub, ReportServiceStub


@pytest.mark.parametrize(("owner", "balance", "accepted"), [
    ("  Ия ", "0", True),
    ("  ", "0", False),
    ("Ия", "-0.01", False),
    ("Ия", "0.01", True),
    ("А" * 80, "0", True),
    ("А" * 81, "0", False),
])
def test_account_validation(owner, balance, accepted):
    if accepted:
        account = AccountCreate(owner=owner, opening_balance=balance)
        assert account.owner == owner.strip()
        assert account.opening_balance == Decimal(balance)
    else:
        with pytest.raises(ValueError):
            AccountCreate(owner=owner, opening_balance=balance)


@pytest.mark.parametrize(("amount", "accepted"), [
    ("-0.01", False), ("0", False), ("0.001", False),
    ("0.01", True), ("125.120", True),
])
def test_amount_validation(amount, accepted):
    if accepted:
        assert AmountRequest(amount=amount).amount == Decimal(amount)
    else:
        with pytest.raises(ValueError):
            AmountRequest(amount=amount)


def test_report_filters_sender_and_recipient():
    report = ReportService()
    operation = HistoryItem(
        transaction_id="TRX-000001", source_account_id="A",
        destination_account_id="B", amount="1.00", status="completed",
    )
    assert report.history("A").operations == []
    report.record(operation)
    assert report.history("A").operations == [operation]
    assert report.history("B").operations == [operation]
    assert report.history("C").operations == []


@pytest.mark.parametrize(("error_type", "status", "code"), [
    (errors.IntegrationError, 500, "integration_error"),
    (errors.InvalidIntegrationDataError, 400, "invalid_data"),
    (errors.AccountNotFoundError, 404, "account_not_found"),
    (errors.InsufficientFundsError, 409, "insufficient_funds"),
    (errors.VersionConflictError, 409, "version_conflict"),
    (errors.ModuleUnavailableError, 503, "module_unavailable"),
    (errors.IntegrationTimeoutError, 504, "integration_timeout"),
])
def test_error_contract(error_type, status, code):
    error = error_type("пояснение")
    assert isinstance(error, errors.IntegrationError)
    assert (error.status_code, error.code, str(error)) == (status, code, "пояснение")


def test_stub_contract():
    stub = AccountServiceStub()
    account = stub.create(AccountCreate(owner="Иван", opening_balance="1.23"))
    assert (account.account_id, account.owner, account.balance) == (
        "ACC-STUB", "Иван", Decimal("1.23"),
    )
    assert stub.get("ACC-0001").account_id == "ACC-0001"
    assert stub.get("ACC-0001").balance == Decimal("1000.00")
    assert stub.deposit("ACC-0001", Decimal("10")).balance == Decimal("1010.00")
    assert stub.withdraw("ACC-0001", Decimal("10")).balance == Decimal("990.00")
    assert ReportServiceStub().history("ACC-0001").model_dump() == {
        "schema_version": "1.0", "account_id": "ACC-0001", "operations": [],
    }


def test_server_entry_point(monkeypatch):
    calls = []

    def fake_run(app, **options):
        calls.append((app, options))

    monkeypatch.setattr(uvicorn, "run", fake_run)
    runpy.run_module("src.server", run_name="__main__")
    assert calls == [("src.api:app", {"host": "127.0.0.1", "port": 8000, "reload": False})]


def test_importing_server_does_not_bind_port(monkeypatch):
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: pytest.fail("Запуск при импорте"))
    runpy.run_module("src.server")

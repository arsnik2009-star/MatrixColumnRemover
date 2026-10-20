"""Заглушки нижних модулей для первого этапа нисходящей интеграции."""

from decimal import Decimal

from src.models import (
    AccountCreate,
    AccountResponse,
    HistoryResponse,
    TransferResponse,
)


class AccountServiceStub:
    def create(self, data: AccountCreate) -> AccountResponse:
        return AccountResponse(
            account_id="ACC-STUB",
            owner=data.owner,
            balance=data.opening_balance,
        )

    def get(self, account_id: str) -> AccountResponse:
        return AccountResponse(
            account_id=account_id,
            owner="Тестовый клиент",
            balance=Decimal("1000.00"),
        )

    def deposit(self, account_id: str, amount: Decimal) -> AccountResponse:
        return AccountResponse(
            account_id=account_id,
            owner="Тестовый клиент",
            balance=Decimal("1000.00") + amount,
        )

    def withdraw(self, account_id: str, amount: Decimal) -> AccountResponse:
        return AccountResponse(
            account_id=account_id,
            owner="Тестовый клиент",
            balance=Decimal("1000.00") - amount,
        )


class TransactionServiceStub:
    def transfer(self, request) -> TransferResponse:
        return TransferResponse(
            transaction_id="TRX-STUB",
            source_account_id=request.source_account_id,
            destination_account_id=request.destination_account_id,
            amount=request.amount,
            source_balance=Decimal("900.00"),
            destination_balance=Decimal("1100.00"),
        )


class ReportServiceStub:
    def history(self, account_id: str) -> HistoryResponse:
        return HistoryResponse(account_id=account_id, operations=[])

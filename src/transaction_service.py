"""Переводы денежных средств между счетами."""

from itertools import count

from src.errors import InvalidIntegrationDataError
from src.models import HistoryItem, TransferRequest, TransferResponse


class TransactionService:
    def __init__(self, account_service, report_service):
        self.account_service = account_service
        self.report_service = report_service
        self._numbers = count(1)

    def transfer(self, request: TransferRequest) -> TransferResponse:
        if request.source_account_id == request.destination_account_id:
            raise InvalidIntegrationDataError("счета отправителя и получателя совпадают")

        source = self.account_service.withdraw(
            request.source_account_id,
            request.amount,
        )
        try:
            destination = self.account_service.deposit(
                request.destination_account_id,
                request.amount,
            )
        except Exception:
            self.account_service.deposit(request.source_account_id, request.amount)
            raise

        transaction_id = f"TRX-{next(self._numbers):06d}"
        operation = HistoryItem(
            transaction_id=transaction_id,
            source_account_id=request.source_account_id,
            destination_account_id=request.destination_account_id,
            amount=request.amount,
            status="completed",
        )
        self.report_service.record(operation)
        return TransferResponse(
            transaction_id=transaction_id,
            source_account_id=request.source_account_id,
            destination_account_id=request.destination_account_id,
            amount=request.amount,
            source_balance=source.balance,
            destination_balance=destination.balance,
        )

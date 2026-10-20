"""Формирование истории банковских операций."""

from src.models import HistoryItem, HistoryResponse, API_VERSION


class ReportService:
    def __init__(self):
        self._operations: list[HistoryItem] = []

    def record(self, operation: HistoryItem) -> None:
        self._operations.append(operation)

    def history(self, account_id: str) -> HistoryResponse:
        operations = [
            operation
            for operation in self._operations
            if account_id in (
                operation.source_account_id,
                operation.destination_account_id,
            )
        ]
        return HistoryResponse(
            schema_version=API_VERSION,
            account_id=account_id,
            operations=operations,
        )

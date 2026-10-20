"""Демонстрация первого этапа нисходящей интеграции."""

from src.integration import BankingProcessor
from src.models import TransferRequest
from src.stubs import AccountServiceStub, ReportServiceStub, TransactionServiceStub


processor = BankingProcessor(
    AccountServiceStub(),
    TransactionServiceStub(),
    ReportServiceStub(),
)
result = processor.transfer(TransferRequest(
    source_account_id="ACC-0001",
    destination_account_id="ACC-0002",
    amount="100.00",
))
print(result.model_dump_json(indent=2))

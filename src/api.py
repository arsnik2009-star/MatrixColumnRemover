"""REST API интегрированной банковской системы."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.account_service import AccountService
from src.errors import IntegrationError
from src.integration import BankingProcessor
from src.models import (
    API_VERSION,
    AccountCreate,
    AccountResponse,
    AmountRequest,
    HistoryResponse,
    TransferRequest,
    TransferResponse,
)
from src.report_service import ReportService
from src.transaction_service import TransactionService


def create_app(account_service=None, transaction_service=None, report_service=None) -> FastAPI:
    accounts = account_service or AccountService()
    reports = report_service or ReportService()
    transactions = transaction_service or TransactionService(accounts, reports)
    processor = BankingProcessor(accounts, transactions, reports)

    app = FastAPI(title="Учебная банковская система", version=API_VERSION)

    @app.exception_handler(IntegrationError)
    async def integration_error_handler(request: Request, error: IntegrationError):
        return JSONResponse(
            status_code=error.status_code,
            content={
                "error": error.code,
                "message": str(error),
                "path": request.url.path,
            },
        )

    @app.get("/health")
    def health():
        return {"status": "ok", "schema_version": API_VERSION}

    @app.post("/api/v1/accounts", response_model=AccountResponse, status_code=201)
    def create_account(data: AccountCreate):
        return accounts.create(data)

    @app.get("/api/v1/accounts/{account_id}", response_model=AccountResponse)
    def get_account(account_id: str):
        return accounts.get(account_id)

    @app.post("/api/v1/accounts/{account_id}/deposit", response_model=AccountResponse)
    def deposit(account_id: str, data: AmountRequest):
        return accounts.deposit(account_id, data.amount)

    @app.post("/api/v1/accounts/{account_id}/withdraw", response_model=AccountResponse)
    def withdraw(account_id: str, data: AmountRequest):
        return accounts.withdraw(account_id, data.amount)

    @app.post("/api/v1/transfers", response_model=TransferResponse)
    def transfer(data: TransferRequest, timeout: float = 2.0):
        return processor.transfer(data, timeout_seconds=timeout)

    @app.get("/api/v1/accounts/{account_id}/history", response_model=HistoryResponse)
    def history(account_id: str):
        accounts.get(account_id)
        return reports.history(account_id)

    return app


app = create_app()

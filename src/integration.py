"""Интеграционный слой банковских модулей."""

from concurrent.futures import ThreadPoolExecutor, TimeoutError

from src.errors import (
    IntegrationError,
    IntegrationTimeoutError,
    ModuleUnavailableError,
    VersionConflictError,
)
from src.models import API_VERSION, TransferRequest


class BankingProcessor:
    def __init__(self, account_service, transaction_service, report_service):
        if any(service is None for service in (
            account_service,
            transaction_service,
            report_service,
        )):
            raise ModuleUnavailableError("не передан обязательный модуль")
        self.account_service = account_service
        self.transaction_service = transaction_service
        self.report_service = report_service

    def transfer(self, request: TransferRequest, timeout_seconds: float = 2.0):
        if request.schema_version != API_VERSION:
            raise VersionConflictError(
                f"версия {request.schema_version} не поддерживается; ожидается {API_VERSION}"
            )
        if timeout_seconds <= 0:
            raise IntegrationTimeoutError("таймаут должен быть положительным")

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.transaction_service.transfer, request)
        try:
            return future.result(timeout=timeout_seconds)
        except TimeoutError as error:
            future.cancel()
            raise IntegrationTimeoutError("превышено время выполнения перевода") from error
        except IntegrationError:
            raise
        except Exception as error:
            raise ModuleUnavailableError("модуль транзакций недоступен") from error
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

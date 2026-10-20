"""Ошибки интеграции банковских модулей."""


class IntegrationError(Exception):
    """Базовая ошибка, безопасно возвращаемая через REST API."""

    code = "integration_error"
    status_code = 500


class InvalidIntegrationDataError(IntegrationError):
    code = "invalid_data"
    status_code = 400


class AccountNotFoundError(IntegrationError):
    code = "account_not_found"
    status_code = 404


class InsufficientFundsError(IntegrationError):
    code = "insufficient_funds"
    status_code = 409


class VersionConflictError(IntegrationError):
    code = "version_conflict"
    status_code = 409


class ModuleUnavailableError(IntegrationError):
    code = "module_unavailable"
    status_code = 503


class IntegrationTimeoutError(IntegrationError):
    code = "integration_timeout"
    status_code = 504

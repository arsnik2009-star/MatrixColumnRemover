"""Создание счетов, пополнение и снятие средств."""

from decimal import Decimal, ROUND_HALF_UP
from itertools import count
from threading import RLock

from src.errors import AccountNotFoundError, InsufficientFundsError
from src.models import AccountCreate, AccountResponse, API_VERSION


MONEY_STEP = Decimal("0.01")


def as_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_STEP, rounding=ROUND_HALF_UP)


class AccountService:
    """Хранилище счетов в памяти для учебного REST-сервиса."""

    def __init__(self):
        self._accounts: dict[str, dict[str, object]] = {}
        self._numbers = count(1)
        self._lock = RLock()

    def create(self, data: AccountCreate) -> AccountResponse:
        with self._lock:
            account_id = f"ACC-{next(self._numbers):04d}"
            self._accounts[account_id] = {
                "owner": data.owner,
                "balance": as_money(data.opening_balance),
            }
            return self.get(account_id)

    def get(self, account_id: str) -> AccountResponse:
        try:
            account = self._accounts[account_id]
        except KeyError as error:
            raise AccountNotFoundError(f"счёт {account_id} не найден") from error
        return AccountResponse(
            schema_version=API_VERSION,
            account_id=account_id,
            owner=str(account["owner"]),
            balance=account["balance"],
        )

    def deposit(self, account_id: str, amount: Decimal) -> AccountResponse:
        with self._lock:
            current = self.get(account_id)
            self._accounts[account_id]["balance"] = as_money(current.balance + amount)
            return self.get(account_id)

    def withdraw(self, account_id: str, amount: Decimal) -> AccountResponse:
        with self._lock:
            current = self.get(account_id)
            if current.balance < amount:
                raise InsufficientFundsError("недостаточно средств на счёте")
            self._accounts[account_id]["balance"] = as_money(current.balance - amount)
            return self.get(account_id)

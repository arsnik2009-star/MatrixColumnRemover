# Интеграция банковских модулей

## Архитектура

Клиент передаёт JSON в REST API. API проверяет структуру сообщения и вызывает `BankingProcessor`. Интеграционный слой контролирует версию контракта и время выполнения, после чего передаёт запрос модулю транзакций. Модуль транзакций вызывает модуль счетов и передаёт завершённую операцию модулю отчёта.

Поток данных:

`HTTP-клиент -> REST API -> BankingProcessor -> TransactionService -> AccountService -> ReportService`

## Порядок нисходящей интеграции

1. Создан внешний REST-маршрут и модели JSON.
2. Подключены `AccountServiceStub`, `TransactionServiceStub` и `ReportServiceStub`.
3. Заглушка счетов заменена рабочим `AccountService`.
4. Подключён `TransactionService`.
5. Подключён `ReportService` и проверен полный сценарий.

## REST-контракт

- `POST /api/v1/accounts` - создать счёт;
- `POST /api/v1/accounts/{id}/deposit` - пополнить счёт;
- `POST /api/v1/accounts/{id}/withdraw` - снять средства;
- `POST /api/v1/transfers` - выполнить перевод;
- `GET /api/v1/accounts/{id}/history` - получить историю;
- `GET /health` - проверить доступность.

Тип содержимого запросов и ответов - `application/json`. Версия схемы передаётся в поле `schema_version` и равна `1.0`.

## Пример перевода

```json
{
  "schema_version": "1.0",
  "source_account_id": "ACC-0001",
  "destination_account_id": "ACC-0002",
  "amount": "125.00"
}
```

Успешный ответ содержит идентификатор транзакции, сумму и новые остатки обоих счетов.

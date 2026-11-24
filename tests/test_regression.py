"""Регрессии по дефектам ЛР №4."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from src.api import create_app
from src.matrix_column_remover import validate_matrix


@pytest.mark.regression
def test_short_owner_after_trimming_is_rejected():
    with TestClient(create_app()) as api:
        response = api.post("/api/v1/accounts", json={"owner": " А "})
    assert response.status_code == 422


@pytest.mark.regression
def test_fractional_cent_transfer_leaves_balances_unchanged():
    with TestClient(create_app()) as api:
        source = api.post("/api/v1/accounts", json={
            "owner": "Иван", "opening_balance": "1.00",
        }).json()["account_id"]
        target = api.post("/api/v1/accounts", json={
            "owner": "Анна", "opening_balance": "1.00",
        }).json()["account_id"]
        response = api.post("/api/v1/transfers", json={
            "source_account_id": source, "destination_account_id": target, "amount": "0.005",
        })
        balances = [
            Decimal(api.get(f"/api/v1/accounts/{account}").json()["balance"])
            for account in (source, target)
        ]
        operations = api.get(f"/api/v1/accounts/{source}/history").json()["operations"]
    assert (response.status_code, balances, operations) == (422, [Decimal("1.00")] * 2, [])


@pytest.mark.regression
def test_matrix_with_empty_first_row_is_not_rectangular():
    with pytest.raises(ValueError, match="одинаковую длину"):
        validate_matrix([[], [1.0]])

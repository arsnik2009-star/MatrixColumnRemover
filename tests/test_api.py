"""Проверка REST API и формата JSON."""

from fastapi.testclient import TestClient

from src.api import create_app


def client():
    return TestClient(create_app())


def create_account(api, owner, balance):
    response = api.post(
        "/api/v1/accounts",
        json={"owner": owner, "opening_balance": balance},
    )
    assert response.status_code == 201
    return response.json()


def test_health():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "schema_version": "1.0"}


def test_full_rest_scenario():
    api = client()
    source = create_account(api, "Иван", "500.00")
    destination = create_account(api, "Мария", "50.00")
    response = api.post(
        "/api/v1/transfers",
        json={
            "schema_version": "1.0",
            "source_account_id": source["account_id"],
            "destination_account_id": destination["account_id"],
            "amount": "125.00",
        },
    )
    assert response.status_code == 200
    assert response.json()["source_balance"] == "375.00"
    history = api.get(f"/api/v1/accounts/{source['account_id']}/history")
    assert len(history.json()["operations"]) == 1


def test_deposit_and_withdraw():
    api = client()
    account = create_account(api, "Иван", "100.00")
    account_id = account["account_id"]
    assert api.post(
        f"/api/v1/accounts/{account_id}/deposit",
        json={"amount": "50.00"},
    ).json()["balance"] == "150.00"
    assert api.post(
        f"/api/v1/accounts/{account_id}/withdraw",
        json={"amount": "20.00"},
    ).json()["balance"] == "130.00"


def test_validation_error():
    response = client().post(
        "/api/v1/accounts",
        json={"owner": "", "opening_balance": "-1"},
    )
    assert response.status_code == 422


def test_account_not_found_error():
    response = client().get("/api/v1/accounts/ACC-9999")
    assert response.status_code == 404
    assert response.json()["error"] == "account_not_found"


def test_insufficient_funds_error():
    api = client()
    account = create_account(api, "Иван", "10.00")
    response = api.post(
        f"/api/v1/accounts/{account['account_id']}/withdraw",
        json={"amount": "11.00"},
    )
    assert response.status_code == 409
    assert response.json()["error"] == "insufficient_funds"


def test_version_conflict_error():
    api = client()
    source = create_account(api, "Иван", "100.00")
    destination = create_account(api, "Мария", "0.00")
    response = api.post(
        "/api/v1/transfers",
        json={
            "schema_version": "2.0",
            "source_account_id": source["account_id"],
            "destination_account_id": destination["account_id"],
            "amount": "10.00",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"] == "version_conflict"


def test_timeout_error():
    api = client()
    source = create_account(api, "Иван", "100.00")
    destination = create_account(api, "Мария", "0.00")
    response = api.post(
        "/api/v1/transfers?timeout=0",
        json={
            "source_account_id": source["account_id"],
            "destination_account_id": destination["account_id"],
            "amount": "10.00",
        },
    )
    assert response.status_code == 504
    assert response.json()["error"] == "integration_timeout"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_invoice():
    resp = client.post(
        "/accounting/invoices",
        json={
            "customer_id": "cust-1",
            "amount": 120.5,
            "currency": "ILS",
            "description": "Managed services",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "created"
    assert body["provider"] == "approved-third-party"


def test_remote_session_for_one_time_customer():
    resp = client.post("/rmm/remote-session/ep-2")
    assert resp.status_code == 200
    assert resp.json()["session_status"] == "started"

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db import engine
from app.main import app
from app.models import Ticket

client = TestClient(app, headers={"X-API-Key": "test-key"})


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_missing_api_key_rejected():
    resp = client.get("/customers", headers={"X-API-Key": ""})
    assert resp.status_code == 401


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


def test_register_customer_and_endpoint():
    resp = client.post(
        "/customers", json={"name": "New Co", "customer_type": "recurring"}
    )
    assert resp.status_code == 200
    customer_id = resp.json()["id"]

    resp = client.post(
        "/rmm/endpoints", json={"customer_id": customer_id, "hostname": "newco-01"}
    )
    assert resp.status_code == 200
    endpoint_id = resp.json()["id"]

    resp = client.post(
        f"/rmm/endpoints/{endpoint_id}/heartbeat", json={"pending_patches": 3}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["pending_patches"] == 3
    assert body["status"] == "online"
    assert body["last_seen"] is not None

    resp = client.get("/rmm/patches")
    hostnames = [p["hostname"] for p in resp.json()]
    assert "newco-01" in hostnames


def test_script_task_queue_and_result():
    resp = client.post("/rmm/endpoints/ep-1/tasks", json={"command": "Get-Service"})
    assert resp.status_code == 200
    task = resp.json()
    assert task["status"] == "queued"

    resp = client.get("/rmm/endpoints/ep-1/tasks")
    assert any(t["id"] == task["id"] for t in resp.json())

    resp = client.post(
        f"/rmm/tasks/{task['id']}/result",
        json={"status": "completed", "output": "ok", "exit_code": 0},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    assert body["exit_code"] == 0


def test_ticket_lifecycle_with_sla_and_comments():
    resp = client.post(
        "/psa/tickets",
        json={
            "customer_id": "cust-1",
            "subject": "Printer down",
            "description": "Office printer offline",
            "priority": "low",
        },
    )
    assert resp.status_code == 200
    ticket = resp.json()
    original_due_at = ticket["due_at"]
    assert original_due_at is not None

    resp = client.patch(
        f"/psa/tickets/{ticket['id']}",
        json={"status": "in_progress", "assignee": "tech1", "priority": "urgent"},
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["status"] == "in_progress"
    assert updated["assignee"] == "tech1"
    assert updated["due_at"] != original_due_at

    resp = client.post(
        f"/psa/tickets/{ticket['id']}/comments",
        json={"author": "tech1", "body": "Investigating the issue"},
    )
    assert resp.status_code == 200

    resp = client.get(f"/psa/tickets/{ticket['id']}/comments")
    assert len(resp.json()) == 1
    assert resp.json()[0]["author"] == "tech1"


def test_overdue_tickets():
    resp = client.post(
        "/psa/tickets",
        json={
            "customer_id": "cust-1",
            "subject": "Overdue check",
            "description": "should become overdue",
            "priority": "urgent",
        },
    )
    ticket_id = resp.json()["id"]

    with Session(engine) as session:
        ticket = session.get(Ticket, ticket_id)
        ticket.due_at = datetime.utcnow() - timedelta(hours=1)
        session.add(ticket)
        session.commit()

    resp = client.get("/psa/tickets/overdue")
    ids = [t["id"] for t in resp.json()]
    assert ticket_id in ids


def test_open_only_filter_excludes_closed_tickets():
    resp = client.post(
        "/psa/tickets",
        json={
            "customer_id": "cust-1",
            "subject": "Will be closed",
            "description": "closing soon",
        },
    )
    ticket_id = resp.json()["id"]
    client.patch(f"/psa/tickets/{ticket_id}", json={"status": "closed"})

    resp = client.get("/psa/tickets", params={"open_only": True})
    ids = [t["id"] for t in resp.json()]
    assert ticket_id not in ids

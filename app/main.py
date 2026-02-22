from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.models import (
    Customer,
    CustomerType,
    Endpoint,
    InvoiceRequest,
    Ticket,
)
from integrations.bank_provider import BankingAggregator
from integrations.invoicing_provider import ApprovedThirdPartyInvoicing

app = FastAPI(title="MSP Unified Platform", version="0.1.0")

invoicing = ApprovedThirdPartyInvoicing()
banking = BankingAggregator()

customers: dict[str, Customer] = {
    "cust-1": Customer(id="cust-1", name="Acme Ltd", customer_type=CustomerType.recurring),
    "cust-ot-1": Customer(id="cust-ot-1", name="One-Time Client", customer_type=CustomerType.one_time),
}

endpoints: dict[str, Endpoint] = {
    "ep-1": Endpoint(id="ep-1", customer_id="cust-1", hostname="acme-win-01"),
    "ep-2": Endpoint(id="ep-2", customer_id="cust-ot-1", hostname="ot-laptop-01"),
}

tickets: dict[str, Ticket] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/customers")
def list_customers() -> list[Customer]:
    return list(customers.values())


@app.get("/rmm/endpoints")
def list_endpoints(customer_id: str | None = None) -> list[Endpoint]:
    if not customer_id:
        return list(endpoints.values())
    return [e for e in endpoints.values() if e.customer_id == customer_id]


@app.post("/rmm/remote-session/{endpoint_id}")
def start_remote_session(endpoint_id: str) -> dict[str, str]:
    endpoint = endpoints.get(endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="endpoint not found")

    customer = customers.get(endpoint.customer_id)
    if not customer or not customer.allow_remote_control:
        raise HTTPException(status_code=403, detail="remote control not allowed")

    return {
        "endpoint_id": endpoint_id,
        "session_status": "started",
        "message": "secure remote control session created",
    }


@app.get("/edr/alerts")
def edr_alerts() -> list[dict[str, str]]:
    alerts = []
    for ep in endpoints.values():
        if ep.security_state != "clean":
            alerts.append({"endpoint_id": ep.id, "severity": ep.security_state})
    return alerts


@app.get("/backup/status")
def backup_status() -> list[dict[str, str]]:
    return [{"endpoint_id": ep.id, "backup_state": ep.backup_state} for ep in endpoints.values()]


@app.post("/psa/tickets")
def create_ticket(ticket: Ticket) -> Ticket:
    if ticket.customer_id not in customers:
        raise HTTPException(status_code=404, detail="customer not found")
    tickets[ticket.id] = ticket
    return ticket


@app.get("/psa/tickets")
def list_tickets(open_only: bool = False) -> list[Ticket]:
    data = list(tickets.values())
    if open_only:
        data = [t for t in data if t.is_open]
    return data


@app.post("/accounting/banks/sync/{customer_id}")
def sync_bank(customer_id: str):
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="customer not found")
    return banking.sync_transactions(customer_id)


@app.post("/accounting/invoices")
def create_invoice(payload: InvoiceRequest):
    if payload.customer_id not in customers:
        raise HTTPException(status_code=404, detail="customer not found")
    return invoicing.create_invoice(payload)

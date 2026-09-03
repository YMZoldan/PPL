from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from app.auth import require_api_key
from app.db import get_session, init_db, seed_demo_data
from app.models import (
    BankSyncResponse,
    CommentCreate,
    Customer,
    CustomerCreate,
    Endpoint,
    EndpointCreate,
    EndpointStatus,
    HeartbeatRequest,
    InvoiceRequest,
    InvoiceResponse,
    ScriptTask,
    ScriptTaskCreate,
    ScriptTaskResult,
    SecurityState,
    Ticket,
    TicketComment,
    TicketCreate,
    TicketStatus,
    TicketUpdate,
)
from integrations.bank_provider import BankingAggregator
from integrations.invoicing_provider import ApprovedThirdPartyInvoicing

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_demo_data()
    yield


app = FastAPI(title="MSP Unified Platform", version="0.2.0", lifespan=lifespan)

invoicing = ApprovedThirdPartyInvoicing()
banking = BankingAggregator()

CLOSED_STATUSES = {TicketStatus.resolved, TicketStatus.closed}

api = APIRouter(dependencies=[Depends(require_api_key)])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _get_customer_or_404(session: Session, customer_id: str) -> Customer:
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")
    return customer


def _get_endpoint_or_404(session: Session, endpoint_id: str) -> Endpoint:
    endpoint = session.get(Endpoint, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="endpoint not found")
    return endpoint


def _get_ticket_or_404(session: Session, ticket_id: str) -> Ticket:
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="ticket not found")
    return ticket


@api.get("/customers")
def list_customers(session: Session = Depends(get_session)) -> list[Customer]:
    return list(session.exec(select(Customer)).all())


@api.post("/customers")
def create_customer(payload: CustomerCreate, session: Session = Depends(get_session)) -> Customer:
    customer = Customer(**payload.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@api.get("/rmm/endpoints")
def list_endpoints(
    customer_id: str | None = None, session: Session = Depends(get_session)
) -> list[Endpoint]:
    stmt = select(Endpoint)
    if customer_id:
        stmt = stmt.where(Endpoint.customer_id == customer_id)
    return list(session.exec(stmt).all())


@api.post("/rmm/endpoints")
def register_endpoint(
    payload: EndpointCreate, session: Session = Depends(get_session)
) -> Endpoint:
    _get_customer_or_404(session, payload.customer_id)
    endpoint = Endpoint(**payload.model_dump())
    session.add(endpoint)
    session.commit()
    session.refresh(endpoint)
    return endpoint


@api.post("/rmm/remote-session/{endpoint_id}")
def start_remote_session(
    endpoint_id: str, session: Session = Depends(get_session)
) -> dict[str, str]:
    endpoint = _get_endpoint_or_404(session, endpoint_id)
    customer = session.get(Customer, endpoint.customer_id)
    if not customer or not customer.allow_remote_control:
        raise HTTPException(status_code=403, detail="remote control not allowed")

    return {
        "endpoint_id": endpoint_id,
        "session_status": "started",
        "message": "secure remote control session created",
    }


@api.post("/rmm/endpoints/{endpoint_id}/heartbeat")
def endpoint_heartbeat(
    endpoint_id: str, payload: HeartbeatRequest, session: Session = Depends(get_session)
) -> Endpoint:
    endpoint = _get_endpoint_or_404(session, endpoint_id)
    endpoint.status = EndpointStatus.online
    endpoint.last_seen = datetime.utcnow()
    if payload.security_state is not None:
        endpoint.security_state = payload.security_state
    if payload.backup_state is not None:
        endpoint.backup_state = payload.backup_state
    if payload.pending_patches is not None:
        endpoint.pending_patches = payload.pending_patches
    session.add(endpoint)
    session.commit()
    session.refresh(endpoint)
    return endpoint


@api.post("/rmm/endpoints/{endpoint_id}/tasks")
def queue_script_task(
    endpoint_id: str, payload: ScriptTaskCreate, session: Session = Depends(get_session)
) -> ScriptTask:
    _get_endpoint_or_404(session, endpoint_id)
    task = ScriptTask(endpoint_id=endpoint_id, command=payload.command)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@api.get("/rmm/endpoints/{endpoint_id}/tasks")
def list_endpoint_tasks(
    endpoint_id: str, session: Session = Depends(get_session)
) -> list[ScriptTask]:
    _get_endpoint_or_404(session, endpoint_id)
    stmt = select(ScriptTask).where(ScriptTask.endpoint_id == endpoint_id)
    return list(session.exec(stmt).all())


@api.post("/rmm/tasks/{task_id}/result")
def report_task_result(
    task_id: str, payload: ScriptTaskResult, session: Session = Depends(get_session)
) -> ScriptTask:
    task = session.get(ScriptTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    task.status = payload.status
    task.output = payload.output
    task.exit_code = payload.exit_code
    task.completed_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@api.get("/rmm/patches")
def patch_summary(session: Session = Depends(get_session)) -> list[dict[str, object]]:
    stmt = select(Endpoint).where(Endpoint.pending_patches > 0)
    endpoints = session.exec(stmt).all()
    return [
        {
            "endpoint_id": ep.id,
            "hostname": ep.hostname,
            "pending_patches": ep.pending_patches,
        }
        for ep in endpoints
    ]


@api.get("/edr/alerts")
def edr_alerts(session: Session = Depends(get_session)) -> list[dict[str, str]]:
    endpoints = session.exec(select(Endpoint)).all()
    return [
        {"endpoint_id": ep.id, "severity": ep.security_state}
        for ep in endpoints
        if ep.security_state != SecurityState.clean
    ]


@api.get("/backup/status")
def backup_status(session: Session = Depends(get_session)) -> list[dict[str, str]]:
    endpoints = session.exec(select(Endpoint)).all()
    return [{"endpoint_id": ep.id, "backup_state": ep.backup_state} for ep in endpoints]


@api.post("/psa/tickets")
def create_ticket(payload: TicketCreate, session: Session = Depends(get_session)) -> Ticket:
    _get_customer_or_404(session, payload.customer_id)
    ticket = Ticket(**payload.model_dump())
    ticket.apply_sla()
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@api.get("/psa/tickets/overdue")
def list_overdue_tickets(session: Session = Depends(get_session)) -> list[Ticket]:
    now = datetime.utcnow()
    tickets = session.exec(select(Ticket)).all()
    return [t for t in tickets if t.due_at and t.due_at < now and t.status not in CLOSED_STATUSES]


@api.get("/psa/tickets")
def list_tickets(
    open_only: bool = False, customer_id: str | None = None, session: Session = Depends(get_session)
) -> list[Ticket]:
    stmt = select(Ticket)
    if customer_id:
        stmt = stmt.where(Ticket.customer_id == customer_id)
    tickets = list(session.exec(stmt).all())
    if open_only:
        tickets = [t for t in tickets if t.status not in CLOSED_STATUSES]
    return tickets


@api.get("/psa/tickets/{ticket_id}")
def get_ticket(ticket_id: str, session: Session = Depends(get_session)) -> Ticket:
    return _get_ticket_or_404(session, ticket_id)


@api.patch("/psa/tickets/{ticket_id}")
def update_ticket(
    ticket_id: str, payload: TicketUpdate, session: Session = Depends(get_session)
) -> Ticket:
    ticket = _get_ticket_or_404(session, ticket_id)
    updates = payload.model_dump(exclude_unset=True)
    priority_changed = "priority" in updates
    for field, value in updates.items():
        setattr(ticket, field, value)
    if priority_changed:
        ticket.apply_sla()
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@api.post("/psa/tickets/{ticket_id}/comments")
def add_ticket_comment(
    ticket_id: str, payload: CommentCreate, session: Session = Depends(get_session)
) -> TicketComment:
    _get_ticket_or_404(session, ticket_id)
    comment = TicketComment(ticket_id=ticket_id, **payload.model_dump())
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@api.get("/psa/tickets/{ticket_id}/comments")
def list_ticket_comments(
    ticket_id: str, session: Session = Depends(get_session)
) -> list[TicketComment]:
    _get_ticket_or_404(session, ticket_id)
    stmt = select(TicketComment).where(TicketComment.ticket_id == ticket_id)
    return list(session.exec(stmt).all())


@api.post("/accounting/banks/sync/{customer_id}")
def sync_bank(customer_id: str, session: Session = Depends(get_session)) -> BankSyncResponse:
    _get_customer_or_404(session, customer_id)
    return banking.sync_transactions(customer_id)


@api.post("/accounting/invoices")
def create_invoice(
    payload: InvoiceRequest, session: Session = Depends(get_session)
) -> InvoiceResponse:
    _get_customer_or_404(session, payload.customer_id)
    return invoicing.create_invoice(payload)


app.include_router(api)

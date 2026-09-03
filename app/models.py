from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4

from sqlmodel import Field, SQLModel


def _new_id() -> str:
    return uuid4().hex


class EndpointStatus(str, Enum):
    online = "online"
    offline = "offline"
    degraded = "degraded"


class SecurityState(str, Enum):
    clean = "clean"
    suspicious = "suspicious"
    compromised = "compromised"


class BackupState(str, Enum):
    ok = "ok"
    failed = "failed"
    running = "running"


class CustomerType(str, Enum):
    recurring = "recurring"
    one_time = "one_time"


class TaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


SLA_HOURS: dict[TicketPriority, int] = {
    TicketPriority.urgent: 4,
    TicketPriority.high: 8,
    TicketPriority.medium: 24,
    TicketPriority.low: 72,
}


class Customer(SQLModel, table=True):
    id: str = Field(default_factory=_new_id, primary_key=True)
    name: str
    customer_type: CustomerType
    allow_remote_control: bool = True


class CustomerCreate(SQLModel):
    name: str
    customer_type: CustomerType
    allow_remote_control: bool = True


class Endpoint(SQLModel, table=True):
    id: str = Field(default_factory=_new_id, primary_key=True)
    customer_id: str = Field(foreign_key="customer.id", index=True)
    hostname: str
    status: EndpointStatus = EndpointStatus.online
    security_state: SecurityState = SecurityState.clean
    backup_state: BackupState = BackupState.ok
    pending_patches: int = 0
    last_seen: datetime | None = None


class EndpointCreate(SQLModel):
    customer_id: str
    hostname: str


class HeartbeatRequest(SQLModel):
    security_state: SecurityState | None = None
    backup_state: BackupState | None = None
    pending_patches: int | None = None


class ScriptTask(SQLModel, table=True):
    id: str = Field(default_factory=_new_id, primary_key=True)
    endpoint_id: str = Field(foreign_key="endpoint.id", index=True)
    command: str
    status: TaskStatus = TaskStatus.queued
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    output: str | None = None
    exit_code: int | None = None


class ScriptTaskCreate(SQLModel):
    command: str


class ScriptTaskResult(SQLModel):
    status: TaskStatus
    output: str | None = None
    exit_code: int | None = None


class Ticket(SQLModel, table=True):
    id: str = Field(default_factory=_new_id, primary_key=True)
    customer_id: str = Field(foreign_key="customer.id", index=True)
    subject: str
    description: str
    status: TicketStatus = TicketStatus.open
    priority: TicketPriority = TicketPriority.medium
    assignee: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    due_at: datetime | None = None

    def apply_sla(self) -> None:
        self.due_at = self.created_at + timedelta(hours=SLA_HOURS[self.priority])


class TicketCreate(SQLModel):
    customer_id: str
    subject: str
    description: str
    priority: TicketPriority = TicketPriority.medium


class TicketUpdate(SQLModel):
    status: TicketStatus | None = None
    assignee: str | None = None
    priority: TicketPriority | None = None


class TicketComment(SQLModel, table=True):
    id: str = Field(default_factory=_new_id, primary_key=True)
    ticket_id: str = Field(foreign_key="ticket.id", index=True)
    author: str
    body: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CommentCreate(SQLModel):
    author: str
    body: str


class InvoiceRequest(SQLModel):
    customer_id: str
    amount: float
    currency: str = "ILS"
    description: str


class InvoiceResponse(SQLModel):
    provider: str
    external_invoice_id: str
    status: str


class BankSyncResponse(SQLModel):
    provider: str
    synced_transactions: int
    status: str

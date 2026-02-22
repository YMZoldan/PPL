from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


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


class Endpoint(BaseModel):
    id: str
    customer_id: str
    hostname: str
    status: EndpointStatus = EndpointStatus.online
    security_state: SecurityState = SecurityState.clean
    backup_state: BackupState = BackupState.ok


class Ticket(BaseModel):
    id: str
    customer_id: str
    subject: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_open: bool = True


class InvoiceRequest(BaseModel):
    customer_id: str
    amount: float
    currency: str = "ILS"
    description: str


class InvoiceResponse(BaseModel):
    provider: str
    external_invoice_id: str
    status: str


class BankSyncResponse(BaseModel):
    provider: str
    synced_transactions: int
    status: str


class Customer(BaseModel):
    id: str
    name: str
    customer_type: CustomerType
    allow_remote_control: bool = True

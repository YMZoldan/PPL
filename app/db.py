from __future__ import annotations

import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.models import Customer, CustomerType, Endpoint

DATABASE_URL = os.environ.get("MSP_DATABASE_URL", "sqlite:///./msp.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def seed_demo_data() -> None:
    with Session(engine) as session:
        if session.get(Customer, "cust-1") is None:
            session.add(Customer(id="cust-1", name="Acme Ltd", customer_type=CustomerType.recurring))
        if session.get(Customer, "cust-ot-1") is None:
            session.add(
                Customer(id="cust-ot-1", name="One-Time Client", customer_type=CustomerType.one_time)
            )
        session.commit()

        if session.get(Endpoint, "ep-1") is None:
            session.add(Endpoint(id="ep-1", customer_id="cust-1", hostname="acme-win-01"))
        if session.get(Endpoint, "ep-2") is None:
            session.add(Endpoint(id="ep-2", customer_id="cust-ot-1", hostname="ot-laptop-01"))
        session.commit()

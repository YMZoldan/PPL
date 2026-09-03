from __future__ import annotations

import os
import tempfile

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["MSP_DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["MSP_API_KEY"] = "test-key"

from app.db import init_db, seed_demo_data  # noqa: E402

init_db()
seed_demo_data()

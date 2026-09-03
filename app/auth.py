from __future__ import annotations

import os

from fastapi import Header, HTTPException, status

API_KEY = os.environ.get("MSP_API_KEY", "dev-key")


def require_api_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing API key")

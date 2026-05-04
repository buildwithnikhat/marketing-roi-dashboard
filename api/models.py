# api/models.py
# Response shapes — every endpoint returns same structure

from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

class APIResponse(BaseModel):
    """
    Standard envelope for ALL API responses.

    Every endpoint returns:
    {
        "success": true,
        "data": {...},
        "meta": {"timestamp": "...", "count": 5},
        "error": null
    }

    Why envelope pattern?
    → Client always checks success first
    → Consistent shape = easier frontend code
    → Error handling is predictable
    """
    success: bool = True
    data:    Any  = None
    meta:    Optional[dict] = None
    error:   Optional[str] = None

    @classmethod
    def ok(cls, data: Any, **meta) -> "APIResponse":
        return cls(
            success=True,
            data=data,
            meta={
                "timestamp": datetime.utcnow().isoformat(),
                **meta
            }
        )

    @classmethod
    def fail(cls, error: str) -> "APIResponse":
        return cls(
            success=False,
            error=error,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
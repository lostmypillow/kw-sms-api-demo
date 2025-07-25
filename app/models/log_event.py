from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class LogEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    level: Literal["INFO", "ERROR"]
    service: str = "kw-sms"
    source: str = "api"
    event: str | None = None
    message: str
    user_id: str | None = None
    path: str | None = None
    method: str | None = None
    request_id: str | None = None
    extra: dict[str, Any] = {}
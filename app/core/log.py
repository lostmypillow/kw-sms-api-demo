# app/utils/logging_service.py
import json
import logging
import sys
import traceback
from typing import Literal

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse, Response
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.log_event import LogEvent


class Log:
    _logger = None
    _console = Console(theme=Theme({"log.level": "bold cyan"}))
    _configured = False
    _service_name = "kw-tutor-api"

    EXCLUDE_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/favicon.ico")

    @classmethod
    def _rich_renderer(cls, _, __, event_dict) -> str:  # noqa: ANN001
        timestamp = event_dict.pop("timestamp", "")
        level = event_dict.pop("level", "").lower()
        service = event_dict.pop("service", "")
        message = event_dict.pop("message", "")
        event = event_dict.pop("event", "")
        remaining = {k: v for k, v in event_dict.items() if v is not None}

        header = Text(f"{timestamp} [{level}] ", style="log.level")
        header.append(f" {service}: {event}")
        cls._console.print(header)

        if message:
            cls._console.print(f"↳ {message}", style="bold")

        if remaining:
            cls._console.print(Panel.fit(str(remaining), title="extra"))

        return ""

    @classmethod
    def setup(cls, human_readable: bool = False) -> None:  # noqa: FBT001, FBT002
        if cls._configured:
            return

        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.INFO,
        )

        processors = [
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            structlog.processors.add_log_level,
            cls._rich_renderer if human_readable else structlog.processors.JSONRenderer(),
        ]

        structlog.configure(
            processors=processors,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        )

        cls._logger = structlog.get_logger(cls._service_name).bind(service=cls._service_name)
        cls._configured = True

    @classmethod
    def log(
        cls,
        event: str,
        message: str,
        source: str = "api:undefined",
        level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
        **kwargs,  # noqa: ANN003
    ) -> None:
        if not cls._configured:
            cls.setup(human_readable="dev" in sys.argv)

        log = LogEvent(
            level=level,
            event=event,
            message=message,
            source=source,
            **kwargs,
        )
        cls._logger.info(**log.dict())

    @classmethod
    async def middleware(cls, request: Request, call_next):  # noqa: ANN001, ANN206
        ip = request.client.host
        path = request.url.path
        method = request.method
        user_id = getattr(request.state, "user_id", None)
        skip_logging = any(path.startswith(p) for p in cls.EXCLUDE_PREFIXES)
        try:
            body_bytes = await request.body()
            try:
                body = json.loads(body_bytes)
            except json.JSONDecodeError:
                body = body_bytes.decode("utf-8", errors="replace")  # Fallback to string
        except json.JSONDecodeError:
            body = "<failed to read body>"


        if not skip_logging:
            cls.log(
                event="http_request_started",
                level="INFO",
                source="api:middleware",
                message=f"Started {method} {path}",
                user_id=user_id,
                path=path,
                method=method,
                extra={
                    "ip": ip,
                    "headers": cls._safe_headers(dict(request.headers)),
                    "body": body,
                },
            )

        try:
            response = await call_next(request)

            if not skip_logging:
                cls.log(
                    event="http_request_completed",
                    level="INFO",
                    source="api:middleware",
                    message=f"Completed {method} {path}",
                    user_id=user_id,
                    path=path,
                    method=method,
                    extra={
                        "ip": ip,
                        "status_code": response.status_code,
                        "headers": cls._safe_headers(dict(response.headers)),
                    },
                )

            return response  # noqa: TRY300

        except Exception as e:  # noqa: BLE001
            cls.log(
                event="unhandled_exception",
                level="ERROR",
                source="api:middleware",
                message=str(e),
                user_id=user_id,
                path=path,
                method=method,
                extra={
                    "ip": ip,
                    "request_headers": cls._safe_headers(dict(request.headers)),
                    "stack": traceback.format_exc(),
                },
            )
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    @staticmethod
    def _safe_headers(headers: dict) -> dict:
        return {
            k: v
            for k, v in headers.items()
            if k.lower() not in {"authorization", "cookie", "set-cookie"}
        }

    class _Middleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next) -> Response:  # noqa: ANN001
            return await Log.middleware(request, call_next)

    @classmethod
    def as_middleware(cls):
        return cls._Middleware
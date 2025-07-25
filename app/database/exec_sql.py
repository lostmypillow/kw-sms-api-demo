from pathlib import Path
from typing import Literal

import anyio
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.log import Log


async def exec_sql(
    mode: Literal["commit", "one", "all"],
    command_name: str,
    session: AsyncSession,
    **kwargs,  # noqa: ANN003
) -> dict | list[dict] | None:
    file_path = Path(__file__).resolve().parent / "sql" / f"{command_name}.sql"

    if not Path(file_path).is_file():
        Log.log(
            event="sql_not_found",
            message=f"SQL file does not exist at {file_path}",
            source="api:database:exec_sql",
            level="ERROR",
        )
        raise FileNotFoundError

    try:
        async with await anyio.open_file(file_path, encoding="utf-8") as file_buffer:
            sql_command = await file_buffer.read()
    except Exception:  # noqa: BLE001
        Log.log(
            event="sql_cant_read",
            message=f"Failed to read SQL file from {file_path}",
            source="api:database:exec_sql",
            level="ERROR",
        )

    try:
        result = await session.execute(text(sql_command), kwargs)

        if mode == "commit":
            await session.commit()
            return None

        if mode == "one":
            row = result.fetchone()
            return dict(row._mapping) if row else {}  # noqa: SLF001

        if mode == "all":
            return [dict(row._mapping) for row in result.fetchall()]  # noqa: SLF001
    except (SQLAlchemyError, DBAPIError):
        Log.log(
            event="sql_known_error",
            message="SQLAlchemyError or DBAPIError",
            source="api:database:exec_sql",
            level="ERROR",
        )
        raise
    except Exception:
        Log.log(
            event="sql_unknown_error",
            message="Generic Exception",
            source="api:database:exec_sql",
            level="ERROR",
        )
        raise
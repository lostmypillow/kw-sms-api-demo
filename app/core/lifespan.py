from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI): # noqa: ANN201, ARG001
    from app.database.engine import async_engine  # noqa: PLC0415
    yield
    if async_engine:
        await async_engine.dispose()

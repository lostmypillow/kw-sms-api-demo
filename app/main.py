import faulthandler
import logging
import os
import tomllib
from contextlib import asynccontextmanager
from pathlib import Path as pathlib_Path
from typing import Annotated, cast

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, status
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse
from rich.traceback import install
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import async_engine
from app.database.get_session import get_session
from app.dependencies import decode_big5
from app.handle_sms import handle_sms
from app.models import ErrorResponse, SMSModel
from app.core.config import get_fastapi_config
import app.mock_sms_api as mock_sms
logger = logging.getLogger()


app = FastAPI(**get_fastapi_config())

app.include_router(mock_sms.router)
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.root_path + cast(str, app.openapi_url),
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/swagger_assets/swagger-ui-bundle.js",
        swagger_css_url="/swagger_assets/swagger-ui.css",
        swagger_favicon_url="/swagger_assets/favicon.ico",
    )


@app.get(cast(str, app.swagger_ui_oauth2_redirect_url), include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get(
    "/sms",
    response_class=HTMLResponse,
    response_description="回傳 'Success' HTML",
    tags=["簡訊系統"],
    summary="發送簡訊",
    description="供 VB 應用程式呼叫的簡訊 API",
    responses={
        200: {
            "content": {
                "text/html": {
                    "example": """
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Success</title>
</head>
<body>
    <h1>Success</h1>
</body>
</html>
"""
                }
            },
            "description": "HTML 格式的成功頁面",
        },
        404: {"model": ErrorResponse, "description": "格式錯誤或其他例外"},
    },
)
async def send_sms(
    background_tasks: BackgroundTasks,
    student_id: Annotated[str, Query(description="學生學號")],
    recipient: Annotated[str, Query(description="收件人姓名")],
    phone_number: Annotated[str, Query(description="手機號碼")],
    message_content: Annotated[str, Query(description="簡訊內容")],
    session: Annotated[AsyncSession, Depends(get_session)],
    send_time: Annotated[str | None, Query(description="預約發送時間")] = None,
) -> str:

    try:
        sms_request: SMSModel = SMSModel(
            student_id=student_id,
            recipient=decode_big5(recipient),
            phone_number=phone_number,
            message_content=decode_big5(message_content),
            send_time=send_time,
        )
        logger.info("[SUCCESS] Received request:")
        logger.info(sms_request.model_dump_json(indent=2))

    except Exception as e:
        logger.exception("Error occured")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="格式錯誤或其他例外",
        ) from e

    background_tasks.add_task(handle_sms, sms_request, session)
    logger.info("Added to background task.")

    return """
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Success</title>
</head>
<body>
    <h1>Success</h1>
</body>
</html>
"""

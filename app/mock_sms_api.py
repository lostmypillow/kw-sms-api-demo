import logging  # noqa: D100
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(tags=["Mock SMS Companies"])
logger = logging.getLogger()


class SMSData(BaseModel):  # noqa: D101
    phone_number: str
    message_content: str


@router.get("/smsSend")
async def sms_company_1(  # noqa: ANN201, D103
    username: Annotated[str, Query(description="Username for SMS service")],
    password: Annotated[str, Query(description="Password for SMS service")],
    mobile: Annotated[str, Query(description="Recipient's mobile number")],
    message: Annotated[str, Query(description="Message content to send")],
):
    logger.info(f"[SMS Company 1] Received SMS request: username={username}, mobile={mobile}, message={message}")  # noqa: G004
    if username == "meow1" and password == "meow1":  # noqa: S105
        return {
            "status": "success",
            "message": "SMS request processed for meow1",
            "data": {"username": username, "mobile": mobile, "message": message},
        }
    if username == "meow2" and password == "meow2":  # noqa: S105
        return {
            "status": "success",
            "message": "SMS request processed for meow2",
            "data": {"username": username, "mobile": mobile, "message": message},
        }
    raise HTTPException(status_code=401, detail="Unauthorized or invalid credentials")


@router.get("/sendutf")
async def sms_company_2(  # noqa: ANN201, D103
    Username: Annotated[str, Query(description="Username for UTF SMS service")],  # noqa: N803
    Pwd: Annotated[str, Query(description="Password for UTF SMS service")],  # noqa: N803
    PhoneNo: Annotated[str, Query(description="Recipient's phone number")],  # noqa: N803
    message: Annotated[str, Query(description="Message content (UTF-8) to send")],
):
    logger.info(
        f"[SMS Company 2] Received UTF SMS request: Username={Username}, PhoneNo={PhoneNo}, message={message}"
    )
    if Username == "12345" and Pwd == "ABCDE":  # noqa: S105
        return {
            "status": "success",
            "message": "UTF SMS request processed",
            "data": {"Username": Username, "PhoneNo": PhoneNo, "message": message},
        }
    raise HTTPException(
        status_code=401, detail="Unauthorized or invalid credentials for UTF service"
    )

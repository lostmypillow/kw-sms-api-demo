import logging  # noqa: D100
import random
from pprint import pformat

from bs4 import BeautifulSoup
from httpx import AsyncClient, Response, Timeout
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.exec_sql import exec_sql
from app.database.get_session import get_session
from app.dependencies import return_url_list
from app.models import SMSModel

logger = logging.getLogger("rich")


async def handle_sms(
    data: SMSModel,
    session: AsyncSession,
) -> None:  # noqa: C901, PLR0912
    url_list = return_url_list(data=data)
    preferred_vendor = None

    try:
        # Check if phone number is associated with a preferred vendor
        preferred_vendor = await exec_sql(
            mode="one",
            command_name="get_specified_vendor",
            session=session,
            phone_number=data.phone_number,
        )
    except Exception:
        logger.info(data.model_dump_json(indent=2))
        logger.exception("Error getting preferred vendor")

    # If phone number has preferred vendor, use preferred vendor
    if preferred_vendor and preferred_vendor is not None:
        vendor_id = preferred_vendor.get("限定廠商編號")
        if vendor_id is None or str(vendor_id) == "0":
            logger.warning(
                "preferred_vendor missing key '限定廠商編號': %s",
                preferred_vendor,
            )
            vendor_id = str(random.randint(1, 3))  # noqa: S311
        else:
            vendor_id = str(vendor_id)
        logger.info(f"Phone number {data.phone_number} will go through vendor No. {vendor_id}")  # noqa: G004

    # If message content has http, randomize vendor 1 and 2
    elif data.message_content.find("http") != -1:
        vendor_id = str(random.randint(1, 2))  # noqa: S311
        logger.info(
            f"{data.phone_number} has http in message content, choosing vendor {vendor_id}",  # noqa: G004
        )

        # If none of the above, randomize 1 to 3
    else:
        vendor_id = str(random.randint(1, 3))  # noqa: S311
        logger.info(
            f"{data.phone_number} has no preferred vendor or 'http' in message, choosing: {vendor_id}"
        )  # noqa: E501, G004

    # If it is vendor 1 and 2...
    if vendor_id != "3":
        # ...and if length of message exceeds 7 characters...
        if len(data.message_content) >= 7:
            logger.info(
                f"{data.phone_number} has message that exceeds 7 characters, appending longsms fragment",
            )

            # ...append longsms to url
            url_list[vendor_id] += "&longsms=Y"

            # ...and if send_time is specified...
        if data.send_time is not None:
            logger.info(f"{data.phone_number} sendtime is specified, adding sendtime fragment")

            # append send time to url
            url_list[vendor_id] += f"&sendtime={data.send_time}"

    if vendor_id not in url_list:
        vendor_id = "3"

    logger.info(f"Vendor URL constructed: {url_list[vendor_id]} for {data.phone_number}")
    sms_id = "N/A"
    # With httpx's AsyncClient
    async with AsyncClient(timeout=Timeout(10.0, connect=5.0)) as client:
        # Gets response from sms vendor
        try:
            response: Response = await client.get(url_list[vendor_id])
            # soup = BeautifulSoup(response.text, "html.parser")
            # tag = soup.find("msgid") if vendor_id != "3" else soup.find("msg")
            logger.info(response.json())
            return
            sms_id = tag.text if tag else "NOT_FOUND"
            logger.info(f"Got response from vendor. ID is {sms_id}")
        except Exception as e:
            logger.exception(f"Error response from vendor: {e}")

        # try:
        #     logger.info(
        #         f"FCM URL: https://{settings.notif_api}.x.tw/x/x/x",
        #     )
        #     res_data = {
        #         "student_id": data.student_id,  # noqa: ERA001
        #         "phone": data.phone_number,
        #         "title": "簡訊通知",
        #         "body": data.message_content,
        #     }
        #     res = await client.post(
        #         "https://"
        #         + settings.notif_api
        #         + ".x.tw/api/x/x",
        #         data=res_data,
        #         headers={"Content-Type": "application/x-www-form-urlencoded"},
        #     )
        #     logger.info(f"Res_data variable: {res_data}")
        #     logger.info(pformat(res_data,indent=2))

        # except Exception as e:
        #     logger.exception(f"Error response from x API: {e}")

    try:
        await exec_sql(
            mode="commit",
            command_name="insert_record",
            session=session,
            student_id=data.student_id,
            recipient=data.recipient,
            phone_number=data.phone_number,
            sms_id=sms_id,
            message_content=data.message_content,
            vendor_id=vendor_id,
        )
        logger.info(f"Inserted into db!")
    except Exception as e:
        logger.exception(f"Error inserting into db")

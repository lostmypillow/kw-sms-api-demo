from app.models import SMSModel
import logging
from pprint import pformat
from urllib.parse import unquote
import chardet

logger = logging.getLogger("rich")


def return_url_list(data: SMSModel):
    url_list = {
        "1": f"http://localhost:8000/smsSend?username=meow1&password=meow1&mobile={str(data.phone_number)}&message={str(data.message_content)}",
        "2": f"http://localhost:8000/smsSend?username=meow2&password=meow2&mobile={str(data.phone_number)}&message={str(data.message_content)}",
        "3": f"http://localhost:8000/sendutf?Username=12345&Pwd=ABCDE&PhoneNo={str(data.phone_number)}&message={str(data.message_content)}",
    }
    logger.info(pformat(url_list, indent=2))
    return url_list


def decode_big5(message):
    try:
        decoded_url = unquote(message).encode()
        if decoded_url:

            encoding = chardet.detect(decoded_url)["encoding"]
            logger.info(f"Encoding is {encoding}")
            if encoding:
                result = decoded_url.decode(encoding=encoding)
            else:
                logger.error("encoding is False or undefined")
        else:
            logger.error("decoded_url is False or undefined")
            raise ValueError
    except Exception as e:
        logger.exception("Exception occured!")

    logger.info(f"Decoding success! Message: {result}")
    return result

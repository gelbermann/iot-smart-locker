import logging
from datetime import datetime
from time import sleep
from typing import Dict, Tuple, Union

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.template import loader

from iot_smart_locker_no_docker.lockers.models import QR, BaseQR, Locker, User

logger = logging.getLogger("django")


def find_locker_for_deposit(recipient: User) -> Tuple[Locker, Union[QR, None]]:
    """There should only be one QR per user.
    If one exists, return its locker.
    If one doesn't exist, allocate locker."""
    try:
        qr: QR = QR.objects.get(recipient=recipient)
    except ObjectDoesNotExist:
        # if qr is None:
        return get_unoccupied_locker(), None
    return qr.locker, qr


def get_unoccupied_locker() -> Locker:
    available_lockers: QuerySet = Locker.objects.filter(occupied=False)
    return available_lockers.first()


def occupy_locker(locker: Locker) -> None:
    locker.occupied = True
    locker.save()


def free_locker(locker: Locker) -> None:
    locker.occupied = False
    locker.save()


def send_qr_via_email(qr: BaseQR, target: str):
    message: str = """
      Hi there! A package is waiting for you!
      Please come pick it up from Smart Locker.
    """
    html_message: str = loader.render_to_string(
        "email/package_is_waiting.html", context={"qr": qr}
    )

    send_mail(
        "A package is waiting for you",
        message,
        "smart-locker@iot.com",
        [target],
        html_message=html_message,
        fail_silently=False,
    )


def request_to_open_locker(locker: Locker):
    # implement in ESP side with: https://randomnerdtutorials.com/esp32-web-server-arduino-ide/ ,
    # https://www.youtube.com/watch?v=CpWhlJXKuDg,
    # https://forum.arduino.cc/t/wifiserver-how-to-get-string-on-server-solved/561577/9
    logger.info("")
    logger.info(
        f"=== request_to_open_locker [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] ==="
    )

    hw_ip: str = "http://192.168.43.212"
    url: str = f"{hw_ip}:80"
    data: str = str(locker.id)
    headers: Dict = {"content-type": "text/plain"}

    logger.info(f"Requesting with retry to open locker #{locker.id}")
    retry(request_with_retry, data=data, headers=headers, url=url)


def retry(func, max_attempts: int = 10, delay: float = 0.25, **kwargs):
    for i in range(max_attempts):
        try:
            func(**kwargs)
        except Exception as e:
            logger.warning(f"Attempt #{i+1} failed for func {func.__name__}")
            logger.warning(e.__repr__())
            sleep(delay)
        else:
            return
    logger.warning("All attempts failed!")
    raise ConnectionError()


def request_with_retry(data, headers, url):
    response: requests.Response = requests.post(url, f"prefix_{data}", headers=headers)
    logger.info(f"response status code: {response.status_code}")
    if response.status_code != 200:
        logger.warning("Something failed in communications with HW")
        logger.warning(response.__repr__())

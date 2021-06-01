from typing import Tuple, Union

from django.core.mail import send_mail
from django.db.models import QuerySet
from django.template import loader

from iot_smart_locker_no_docker.lockers.models import QR, BaseQR, Locker, User


def find_locker_for_deposit(recipient: User) -> Tuple[Locker, Union[QR, None]]:
    """There should only be one QR per user.
    If one exists, return its locker.
    If one doesn't exist, allocate locker."""
    qr: QR = QR.objects.get(recipient=recipient)
    if qr is None:
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
    # TODO Send a request for ESP32CAM to open a locker - CONTINUE HERE!!!!
    # implement in ESP side with: https://randomnerdtutorials.com/esp32-web-server-arduino-ide/
    pass

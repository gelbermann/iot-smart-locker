from time import sleep
from typing import List

from django.core.mail import send_mail
from django.db.models import QuerySet
from django.template import loader

from iot_smart_locker_no_docker.lockers.models import BaseQR, Locker


def get_unoccupied_locker():
    available_lockers: QuerySet = Locker.objects.filter(occupied=False)
    return available_lockers.first()


def toggle_locker_status(locker: Locker):
    locker.occupied = not locker.occupied
    locker.save()
    pass


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


def request_to_open_multiple_lockers(lockers: List[Locker]) -> List[Locker]:
    failed_to_open: List[Locker] = []

    for locker in lockers:
        success: bool = request_to_open_locker(locker)
        if not success:
            failed_to_open += locker
        sleep(1)  # give HW time to catch up

    return failed_to_open


def request_to_open_locker(locker: Locker) -> bool:
    # TODO: https://realpython.com/api-integration-in-python/
    #   0) DECIDE WITH TEAM ON API FOR ESP32.
    #   1) send REST request
    #   2) consider waiting for a response.
    #      if waiting, then return value is according to response.
    #      if not waiting, then return value is according to message sent/not sent.
    #   3) remove stub

    # task: Dict = {"TBD": "TBD"}
    # url: str = "TBD"
    # resp: requests.Response = requests.post(url, task)
    # if resp.status_code != 200:
    #     # TODO notify about error somehow
    #     return False

    return _request_to_open_locker_stub()


def _request_to_open_locker_stub():
    return True

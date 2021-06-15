import logging
from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    renderer_classes,
)
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

from .. import utils
from ..models import QR, Locker, User

logger = logging.getLogger("django")


class MessageTexts:
    SUCCESS = "OK"
    FAILED_OPEN_LOCKER = "Failed to open locker {}"
    FAILED_AT_LEAST_ONE = "Some lockers failed to open"


@api_view(("GET",))
@authentication_classes([])
@permission_classes([])  # TODO add "AllowAny"?
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def open_single_locker_with_qr(request, uuid: str):
    # TODO add frontend-access for this view?

    logger.info("")
    logger.info(
        f"=== open_single_locker_with_qr [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] ==="
    )
    logger.info(f"UUID: {uuid}")

    try:
        qr: QR = _find_qr(uuid)
        if qr is None:
            logger.warning(
                f"No QR in database for UUID {uuid}, returning error code 500"
            )
            return HttpResponse(status=500)

        locker: Locker = qr.locker
        logger.info(f"Found relevant locker: #{locker.id}")

        response_code: int = (
            200 + locker.id
        )  # this is our own convention, which the ESP32CAM needs to know how to read
        _cleanup(qr)

    except Exception as e:
        logger.exception(e)
        return HttpResponse(status=500)

    return HttpResponse(status=response_code)


@api_view(("GET",))
@authentication_classes([])
@permission_classes([])  # TODO add "AllowAny"?
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def open_single_locker_with_nfc(request, serial: str):
    # TODO add frontend-access for this view?

    logger.info("")
    logger.info(
        f"=== open_single_locker_with_nfc [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] ==="
    )
    logger.info(f"Serial: {serial}")

    try:
        user: User = _find_user(serial)
        if user is None:
            logger.warning(
                f"No user in database with NFC serial {serial}, returning error code 500"
            )
            return HttpResponse(status=500)

        locker: Locker = _find_locker(user)
        if locker is None:
            logger.warning(
                f"No locker in database waiting for user {user.username}, returning error code 500"
            )
            return HttpResponse(status=500)
        logger.info(f"Found relevant locker: #{locker.id}")

        response_code: int = (
            200 + locker.id
        )  # this is our own convention, which the ESP32CAM needs to know how to read
        _cleanup_by_user(user)

    except Exception as e:
        logger.exception(e)
        return HttpResponse(status=500)

    return HttpResponse(status=response_code)


def show_connection_error_page(request):
    logger.warning("Redirecting user to the connection error page :(")
    return render(request, "500.html")


def _find_user(nfc_serial: str) -> User:
    return User.objects.get(nfc_serial=nfc_serial)


def _find_qr(qr_uuid: str) -> QR:
    return QR.objects.get(uuid=qr_uuid)


def _find_locker(user: User) -> Locker:
    qr: QR = QR.objects.get(recipient=user)
    if qr is None:
        return None
    return qr.locker


def _open_locker(locker_with_package: Locker) -> bool:
    return utils.request_to_open_locker(locker_with_package)


def _handle_response(request, locker: Locker, success: bool) -> int:
    """Handles displaying a response to the user if they request to open a locker using the website"""
    if success:
        return 200 + locker.id

    response: str = MessageTexts.FAILED_OPEN_LOCKER.format(locker.id)
    messages.warning(request, response)
    return 500


def _cleanup_by_user(user: User) -> None:
    qr: QR = QR.objects.get(recipient=user)
    _cleanup(qr)


def _cleanup(consumed_qr: QR) -> None:
    utils.free_locker(consumed_qr.locker)
    consumed_qr.delete()

import logging
from datetime import datetime
from typing import List

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse
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

        success: bool = _open_locker(locker)

        _handle_response(request, locker, success)
        _cleanup(qr)
    except Exception as e:
        logger.exception(e)
        return HttpResponse(status=500)

    return HttpResponse(status=200)


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

        lockers: List[Locker] = _find_lockers(user)
        logger.info(
            f"Found relevant lockers: {' '.join(('#' + str(l.id) for l in lockers))}"
        )

        lockers_failed_to_open: List[Locker] = _open_lockers(lockers)
        if len(lockers_failed_to_open) > 0:
            logger.warning(
                f"Failed to open lockers: {' '.join(('#' + str(l.id) for l in lockers_failed_to_open))}"
            )

        _handle_response_multiple(request, lockers_failed_to_open)
        _cleanup_multiple(list(set(lockers) - set(lockers_failed_to_open)))

    except Exception as e:
        logger.exception(e)
        return HttpResponse(status=500)

    return HttpResponse(status=200)


def _find_user(nfc_serial: str) -> User:
    return User.objects.get(nfc_serial=nfc_serial)


def _find_qr(qr_uuid: str) -> QR:
    return QR.objects.get(uuid=qr_uuid)


def _find_lockers(user: User) -> List[Locker]:
    waiting_packages_qrs: List[QR] = user.qr_set.all()
    lockers_with_package = [qr.locker for qr in waiting_packages_qrs]
    return lockers_with_package


def _open_locker(locker_with_package: Locker) -> bool:
    return utils.request_to_open_locker(locker_with_package)


def _open_lockers(lockers: List[Locker]) -> List[Locker]:
    lockers_failed_to_open: List[Locker] = utils.request_to_open_multiple_lockers(
        lockers
    )
    return lockers_failed_to_open


def _handle_response(request, locker: Locker, success: bool) -> str:
    """Handles displaying a response to the user if they request to open a locker using the website"""
    if not success:
        response: str = MessageTexts.FAILED_OPEN_LOCKER.format(locker.id)
        messages.warning(request, response)
    else:
        response: str = MessageTexts.SUCCESS
    return response


def _handle_response_multiple(request, lockers_failed_to_open: List[Locker]) -> str:
    for locker in lockers_failed_to_open:
        messages.warning(request, MessageTexts.FAILED_OPEN_LOCKER.format(locker.id))
    response: str = (
        MessageTexts.FAILED_AT_LEAST_ONE
        if len(lockers_failed_to_open)
        else MessageTexts.SUCCESS
    )
    return response


def _cleanup(consumed_qr: QR) -> None:
    consumed_qr.locker.occupied = False
    consumed_qr.locker.save()
    consumed_qr.delete()


def _cleanup_multiple(opened_lockers: List[Locker]) -> None:
    consumed_qrs: QuerySet = QR.objects.filter(locker__in=opened_lockers)
    for qr in consumed_qrs:
        _cleanup(qr)

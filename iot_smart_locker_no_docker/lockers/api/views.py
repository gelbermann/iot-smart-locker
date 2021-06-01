import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from django.conf import settings
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    renderer_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import utils
from ..models import QR, Locker, PersonalQR

logger = logging.getLogger("django")


class MessageTexts:
    SUCCESS = "OK"
    FAILURE = "Failed to open locker {}"


@permission_classes((AllowAny,))
class OpenBulkLockersAbstractView(APIView, ABC):
    class MessageTexts:
        SUCCESS = "OK"
        FAILURE = "Some lockers failed to open"
        FAILED_OPEN_LOCKER = "Failed to open locker {}"

    def post(self, request):
        # TODO: extract qr data from the "request.data" dict:
        #  as json, if we go with textual data
        #  or as an image from which we extract the qr and its data, if we go with image streaming
        lockers_with_package: List[Locker] = self._get_lockers_with_packages()
        lockers_failed_to_open: List[Locker] = self._open_lockers(lockers_with_package)
        response = self._handle_response(lockers_failed_to_open)
        self._cleanup(list(set(lockers_with_package) - set(lockers_failed_to_open)))
        return Response(response)

    @abstractmethod
    def _get_lockers_with_packages(self) -> List[Locker]:
        pass

    def _open_lockers(self, lockers_with_package) -> List[Locker]:
        lockers_failed_to_open: List[Locker] = utils.request_to_open_multiple_lockers(
            lockers_with_package
        )
        return lockers_failed_to_open

    def _handle_response(self, lockers_failed_to_open) -> str:
        for locker in lockers_failed_to_open:
            messages.warning(
                self.request, self.MessageTexts.FAILED_OPEN_LOCKER.format(locker.id)
            )
        response: str = (
            self.MessageTexts.FAILURE
            if len(lockers_failed_to_open)
            else self.MessageTexts.SUCCESS
        )
        return response

    def _cleanup(self, opened_lockers: List[Locker]) -> None:
        consumed_qrs: QuerySet = QR.objects.filter(locker__in=opened_lockers)
        consumed_qrs.delete()


class OpenLockersWithPersonalQRView(OpenBulkLockersAbstractView):
    def _get_lockers_with_packages(self) -> List[Locker]:
        if settings.DEBUG:  # TODO remove this if
            recipient_personal_qr: PersonalQR = PersonalQR.objects.first()
        else:
            recipient_personal_qr: PersonalQR = PersonalQR.from_json(
                self.request.session["qr"]
            )

        waiting_packages_qrs: List[QR] = QR.objects.filter(
            recipient=recipient_personal_qr.recipient
        )
        lockers_with_package = [qr.locker for qr in waiting_packages_qrs]
        return lockers_with_package


class OpenLockersWithNFCView(OpenBulkLockersAbstractView):
    def _get_lockers_with_packages(self) -> List[Locker]:
        pass


@api_view(("GET",))
@authentication_classes([])
@permission_classes([])
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def open_single_locker_with_qr(request, uuid: str):
    # TODO add frontend-access for this view?

    logger.info("")
    logger.info(
        f"=== open_single_locker_with_qr [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] ==="
    )
    logger.info(f"UUID: {uuid}")
    # return HttpResponse(status=200)

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

        # response: str = _handle_response(request, locker, success)
        _handle_response(request, locker, success)
        _cleanup(qr)
    except Exception as e:
        logger.exception(e)
        return HttpResponse(status=500)

    # return Response(response)
    return HttpResponse(status=200)


def _find_qr(qr_uuid: str) -> QR:
    qr: QR = QR.objects.get(uuid=qr_uuid)
    return qr


def _open_locker(locker_with_package: Locker) -> bool:
    return utils.request_to_open_locker(locker_with_package)


def _handle_response(request, locker: Locker, success: bool) -> str:
    """Handles displaying a response to the user if they request to open a locker using the website"""
    if not success:
        response: str = MessageTexts.FAILURE.format(locker.id)
        messages.warning(request, response)
    else:
        response: str = MessageTexts.SUCCESS
    return response


def _cleanup(consumed_qr: QR) -> None:
    consumed_qr.locker.occupied = False
    consumed_qr.locker.save()
    consumed_qr.delete()

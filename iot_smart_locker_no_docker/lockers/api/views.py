from abc import ABC, abstractmethod
from typing import List

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import utils
from ..models import QR, Locker, PersonalQR


class OpenBulkLockersAbstractView(LoginRequiredMixin, APIView, ABC):
    class MessageTexts:
        SUCCESS = "OK"
        FAILURE = "Some lockers failed to open"
        FAILED_OPEN_LOCKER = "Failed to open locker {}"

    def get(self, request):
        lockers_with_package: List[Locker] = self._get_lockers_with_packages()
        lockers_failed_to_open: List[Locker] = self._open_lockers(lockers_with_package)
        response = self._determine_response(lockers_failed_to_open)
        self._cleanup(list(set(lockers_with_package) - set(lockers_failed_to_open)))
        return Response(response)

    @abstractmethod
    def _get_lockers_with_packages(self, request) -> List[Locker]:
        pass

    def _open_lockers(self, lockers_with_package) -> List[Locker]:
        lockers_failed_to_open: List[Locker] = utils.request_to_open_multiple_lockers(
            lockers_with_package
        )
        for locker in lockers_failed_to_open:
            messages.warning(
                self.request, self.MessageTexts.FAILED_OPEN_LOCKER.format(locker.id)
            )
        return lockers_failed_to_open

    def _determine_response(self, lockers_failed_to_open) -> str:
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
        if settings.DEBUG:
            recipient_personal_qr: PersonalQR = (
                PersonalQR.objects.first()
            )  # TODO remove this if
        else:
            recipient_personal_qr: PersonalQR = PersonalQR.from_json(self.request["qr"])

        waiting_packages_qrs: List[QR] = QR.objects.filter(
            recipient=recipient_personal_qr.recipient
        )
        lockers_with_package = [qr.locker for qr in waiting_packages_qrs]
        return lockers_with_package


class OpenLockersWithNFCView(OpenBulkLockersAbstractView):
    def _get_lockers_with_packages(self) -> List[Locker]:
        pass

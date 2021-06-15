from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from iot_smart_locker_no_docker.lockers import utils
from iot_smart_locker_no_docker.lockers.forms import LockerDepositForm
from iot_smart_locker_no_docker.lockers.models import QR

User = get_user_model()


class LockerDepositRequestView(LoginRequiredMixin, FormView):
    # TODO link could be useful when implementing predefined QRs:
    #  https://docs.djangoproject.com/en/3.1/topics/class-based-views/generic-editing/#content-negotiation-example

    template_name = "lockers/deposit.html"
    form_class = LockerDepositForm
    success_url = "lockers:deposit_success"  # overrides FormView attribute
    failure_url = "lockers:deposit_failure"  # our own addition

    class MessageTexts:
        NO_LOCKER_AVAILABLE = "No locker is available at the moment 😢"
        REST_ERROR = "Couldn't open a locker at the moment 😢"
        SUCCESS = "Success"

    def form_valid(self, form: LockerDepositForm) -> HttpResponse:
        # generate QR
        recipient_user: User = form.get_recipient_user()
        locker, qr = utils.find_locker_for_deposit(recipient_user)
        if locker is None:
            messages.warning(self.request, self.MessageTexts.NO_LOCKER_AVAILABLE)
            return HttpResponseRedirect(reverse_lazy(self.failure_url))

        if qr is None:  # user doesn't have a waiting locker
            qr: QR = QR(recipient=recipient_user, locker=locker)

        # open locker
        try:
            utils.request_to_open_locker(locker)
        except ConnectionError:
            return HttpResponseRedirect(reverse_lazy("lockers:connection_error"))

        # notify recipient
        utils.send_qr_via_email(qr, recipient_user.email)

        # change locker status to occupied
        utils.occupy_locker(locker)

        qr.save()
        # https://stackoverflow.com/questions/26483026/how-to-pass-context-data-in-success-url
        return HttpResponseRedirect(
            reverse_lazy(self.get_success_url(), kwargs={"qr_id": qr.id})
        )


class LockerDepositSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "lockers/deposit_success.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Customize context here if necessary
        context["qr"] = QR.objects.get(id=context["qr_id"])

        return context

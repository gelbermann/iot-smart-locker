from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from iot_smart_locker_no_docker.lockers import utils
from iot_smart_locker_no_docker.lockers.forms import LockerDepositForm
from iot_smart_locker_no_docker.lockers.models import QR, Locker

User = get_user_model()


# class LockerDetailsView(LoginRequiredMixin, DetailView):
#     # TODO: Use UserPassesTestMixin to enable only for admins
#     model = Locker
#     # TODO: add relevant fields, such as a field for 'occupied'


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

    def form_valid(self, form: LockerDepositForm) -> HttpResponse:
        # generate QR
        recipient_user: User = form.get_recipient_user()
        locker: Locker = utils.get_unoccupied_locker()
        if locker is None:
            messages.warning(self.request, self.MessageTexts.NO_LOCKER_AVAILABLE)
            return HttpResponseRedirect(reverse_lazy(self.failure_url))
        qr: QR = QR.create(recipient_user, locker)

        # TODO:
        #  1) generate QR - V
        #  2) record in history - I think that for now, the Qrs DB table suffices
        #  3) send REST request to open locker - V
        #  4) alert recipient user (with a mail containing either the QR or a link to a page displaying the QR) - V
        #  5) change locker status to occupied - V

        # TODO Also:
        #   1) Add a "general_error.html" page - V
        #   2) Add management API (described in mindmap)

        # open locker
        if not utils.request_to_open_locker(locker):
            messages.warning(self.request, self.MessageTexts.REST_ERROR)
            return HttpResponseRedirect(reverse_lazy(self.failure_url))

        # notify recipient
        utils.send_qr_via_email(qr, recipient_user.email)

        # change locker status to occupied
        utils.toggle_locker_status(locker)

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

from typing import Any, Dict

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
    success_url = "lockers:deposit_success"

    def form_valid(self, form: LockerDepositForm) -> HttpResponse:
        # generate QR
        recipient_user: User = form.get_recipient_user()
        locker: Locker = utils.get_unoccupied_locker()
        qr: QR = QR.create(recipient_user, locker)
        qr.save()

        # TODO:
        #  1) generate QR - V
        #  2) record in history
        #  3) send REST request to open locker
        #  4) alert recipient user (with a mail containing either the QR or a link to a page displaying the QR)
        #  5) change locker status to occupied - V

        # TODO CONTINUE HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE ^^^^^^^ (4)
        #   Also:
        #   1) Add a "deposit_failure.html" page
        #   2) Add management API (described in mindmap)

        # change locker status to occupied
        utils.toggle_locker_status(locker)

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

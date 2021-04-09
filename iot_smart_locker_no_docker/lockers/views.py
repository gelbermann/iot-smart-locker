from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import DetailView, FormView

from iot_smart_locker_no_docker.lockers.forms import LockerDepositForm
from iot_smart_locker_no_docker.lockers.models import Locker


class LockerDetailsView(LoginRequiredMixin, DetailView):
    # TODO: Use UserPassesTestMixin to enable only for admins
    model = Locker
    # TODO: add relevant fields, such as a field for 'occupied'


class LockerDepositRequestView(LoginRequiredMixin, FormView):
    # TODO link could be useful when implementing predefined QRs:
    #  https://docs.djangoproject.com/en/3.1/topics/class-based-views/generic-editing/#content-negotiation-example

    template_name = "lockers/deposit.html"
    form_class = LockerDepositForm
    success_url = "/"  # TODO should probably be something else

    def form_valid(self, form: LockerDepositForm) -> HttpResponse:
        # recipient_user: User = form.get_recipient_user()
        # TODO:
        #  1) generate QR
        #  2) record in history
        #  3) send REST request to open locker
        #  4) alert recipient user
        return super().form_valid(form)  # redirects to `success_url`

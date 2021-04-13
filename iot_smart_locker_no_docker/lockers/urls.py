from django.urls import path
from django.views.generic import TemplateView

from iot_smart_locker_no_docker.lockers.views import (
    LockerDepositRequestView,
    LockerDepositSuccessView,
)

app_name = "lockers"

urlpatterns = [
    path("deposit/", view=LockerDepositRequestView.as_view(), name="deposit"),
    path(
        "deposit/success/<int:qr_id>/",
        view=LockerDepositSuccessView.as_view(),
        name="deposit_success",
    ),
    path(
        "deposit/failure/",
        view=TemplateView.as_view(template_name="lockers/general_error.html"),
        name="deposit_failure",
    ),
]

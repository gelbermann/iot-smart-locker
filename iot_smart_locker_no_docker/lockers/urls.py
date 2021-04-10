from django.urls import path

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
]

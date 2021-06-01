from django.urls import path
from django.views.generic import TemplateView

from iot_smart_locker_no_docker.lockers.api.views import (
    open_single_locker_with_nfc,
    open_single_locker_with_qr,
)
from iot_smart_locker_no_docker.lockers.views import (
    LockerDepositRequestView,
    LockerDepositSuccessView,
)

app_name = "lockers"

urlpatterns = [
    # UI patterns:
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
    # API patterns:
    path(
        "api/collect/qr/<str:uuid>",
        view=open_single_locker_with_qr,
        name="collect_with_qr",
    ),
    # path(
    #     "api/collect/personal_qr/",
    #     view=OpenLockersWithPersonalQRView.as_view(),
    #     name="collect_with_personal_qr",
    # ),
    path(
        "api/collect/nfc/<str:serial>",
        view=open_single_locker_with_nfc,
        name="collect_with_nfc",
    ),
]

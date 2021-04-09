from django.urls import path

from iot_smart_locker_no_docker.lockers.views import LockerDepositRequestView

app_name = "lockers"

urlpatterns = [
    path("deposit/", view=LockerDepositRequestView.as_view(), name="deposit")
]

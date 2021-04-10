from django.contrib import admin

from iot_smart_locker_no_docker.lockers.models import QR, Locker


@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
    """
    Customize here if you want.
    See example in users/admin.py.
    More info: https://docs.djangoproject.com/en/3.2/ref/contrib/admin/
    """

    pass


@admin.register(QR)
class QRAdmin(admin.ModelAdmin):
    pass

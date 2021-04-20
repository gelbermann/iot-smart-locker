from gettext import ngettext

from django.contrib import admin, messages

from iot_smart_locker_no_docker.lockers.forms import (
    PersonalQRChangeForm,
    PersonalQRCreationForm,
    QRChangeForm,
    QRCreationForm,
)
from iot_smart_locker_no_docker.lockers.models import QR, Locker, PersonalQR


@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
    actions = ["free_lockers"]
    list_display = ["id", "occupied"]

    # @admin.action(description="Set selected lockers to 'unoccupied'")    # can only be used in django>=3.2
    def free_lockers(self, request, queryset):
        updated: int = queryset.update(occupied=False)
        self.message_user(
            request,
            ngettext(
                "%d locker was successfully marked as unoccupied.",
                "%d lockers were successfully marked as unoccupied.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    free_lockers.short_description = (
        "Set selected lockers to 'unoccupied'"  # instead of @admin.action(...)
    )


@admin.register(QR)
class QRAdmin(admin.ModelAdmin):
    form = QRChangeForm
    add_form = QRCreationForm
    readonly_fields = ["uuid"]
    list_display = ["recipient", "locker", "uuid"]


@admin.register(PersonalQR)
class PersonalQRAdmin(admin.ModelAdmin):
    form = PersonalQRChangeForm
    add_form = PersonalQRCreationForm
    readonly_fields = ["uuid"]
    list_display = ["recipient", "uuid"]

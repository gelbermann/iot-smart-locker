from typing import Dict, Optional

from allauth.account.models import EmailAddress
from django import forms
from django.contrib.auth.models import User


class LockerDepositForm(forms.Form):
    recipient_email = forms.EmailField(
        label="Recipient Email Address",
        help_text="recipient@example.com",
        max_length=100,
    )

    def is_valid(self) -> bool:
        return (
            super().is_valid()
            and self._recipient_exists()
            and self._user_is_allowed_to_deposit()
        )

    def _recipient_exists(self) -> bool:
        return self.get_recipient_user() is not None

    def get_recipient_user(self) -> Optional[User]:
        data: Dict = self.cleaned_data
        recipient_email: EmailAddress = EmailAddress.objects.filter(
            email=data["recipient_email"]
        ).first()
        return None if recipient_email is None else recipient_email.user

    @staticmethod
    def _user_is_allowed_to_deposit():
        # TODO after adding user permissions/custom user model, for registering delivery men,
        #  update method to check if the user who made the request has permission to make a deposit
        #  (another option: allow access to the "deposit" page only to users with permission
        return True

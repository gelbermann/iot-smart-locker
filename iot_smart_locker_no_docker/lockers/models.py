import json
import uuid
from typing import Dict, Type

import segno
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Model

User: Type[Model] = get_user_model()


class Locker(models.Model):
    occupied = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.id}"


class BaseQR(models.Model):
    class Meta:
        abstract = True

    uuid = models.CharField(default="", max_length=50, unique=True)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )  # TODO what should be the on_delete policy?

    def save(self, *args, **kwargs) -> None:
        self.uuid = uuid.uuid4().hex
        super().save(*args, **kwargs)

    @property
    def qr(self):
        # return qrcode.make(self.to_json()).get_image()
        return segno.make(self.to_json())

    def to_json(self):
        return json.dumps(self._get_json_dumpable())

    def _get_json_dumpable(self):
        return {
            "uuid": self.uuid,
            "recipient_id": self.recipient.id,
        }

    @staticmethod
    def from_json(string):
        data: Dict = json.loads(string)
        unpacked_user: User = User.objects.filter(id=data["recipient_id"]).first()
        return BaseQR.create(unpacked_user)


class PersonalQR(BaseQR):
    recipient = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # TODO what should be the on_delete policy?
    )  # different from BaseQR.recipient by being a OneToOneField (which is the same as a ForeignKey with unique=True

    @staticmethod
    def create(recipient: User, *args, **kwargs):
        return PersonalQR(uuid=uuid.uuid4().hex, recipient=recipient)


class QR(BaseQR):
    locker = models.ForeignKey(
        Locker, on_delete=models.PROTECT
    )  # TODO what should be the on_delete policy?

    def _get_json_dumpable(self) -> Dict:
        data: Dict = super()._get_json_dumpable()
        data["locker_id"] = self.locker.id
        return data

    @staticmethod
    def from_json(string):
        data = json.loads(string)
        unpacked_user = User.objects.filter(id=data["recipient_id"]).first()
        unpacked_locker = Locker.objects.filter(id=data["locker_id"])
        return QR.create(unpacked_user, unpacked_locker)

import json
import uuid

import segno
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Locker(models.Model):
    occupied = models.BooleanField(default=False)


class QR(models.Model):
    uuid = models.CharField(default="", max_length=50)
    recipient = models.ForeignKey(
        # TODO is `recipient` necessary? they display the QR to a camera, they don't do anything on the site itself
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )  # TODO on_delete=?
    locker = models.ForeignKey(Locker, on_delete=models.PROTECT)  # TODO on_delete=?

    @staticmethod
    def create(recipient: User, locker: Locker):
        return QR(uuid=uuid.uuid4().hex, recipient=recipient, locker=locker)

    @property
    def qr(self):
        # return qrcode.make(self.to_json()).get_image()
        return segno.make(self.to_json())

    def to_json(self):
        return json.dumps(
            {
                "uuid": self.uuid,
                "recipient_id": self.recipient.id,
                "locker_id": self.locker.id,
            }
        )

    @staticmethod
    def from_json(string):
        data = json.loads(string)
        unpacked_user = User.objects.filter(id=data["recipient_id"]).first()
        unpacked_locker = Locker.objects.filter(id=data["locker_id"])
        return QR.create(unpacked_user, unpacked_locker)


# class History(models.Model):
#     pass
#     """
#     Each row is a request to open a locker (for a depositor only? or for withdrawals too?)
#
#     TODO
#       Possible fields:
#         Fk to Locker
#         Unique identifier which was included in the QR (timestamp?)
#         User which prompted this history row (e.g. user who requested a locker to deposit in)
#     """

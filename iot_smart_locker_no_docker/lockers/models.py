from django.db import models


class Locker(models.Model):
    occupied = models.BooleanField(default=False)


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

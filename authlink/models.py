from django.conf import settings
from django.db import models

from .utils import generate_authlink_key, get_timezone_now


class AuthLink(models.Model):
    """
    Storage for a pre-authenticated link
    """

    key = models.CharField(
        primary_key=True,
        default=generate_authlink_key,
        editable=False,
        max_length=getattr(settings, "AUTHLINK_KEY_LENGTH", 64),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.TextField()
    ipaddress = models.GenericIPAddressField()
    created = models.DateTimeField(default=get_timezone_now)
    expires = models.DateTimeField()
    used = models.DateTimeField(null=True, blank=True)

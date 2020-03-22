import string

from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string


# we use this so we can easily mock timezone.now() on model fields
# and so that the function can be serialized properly for migrations
# as lambdas cannot be
def get_timezone_now():
    return timezone.now()


VALID_KEY_CHARS = string.ascii_lowercase + string.digits


def generate_authlink_key():
    return get_random_string(
        getattr(settings, "AUTHLINK_KEY_LENGTH", 64), VALID_KEY_CHARS
    )

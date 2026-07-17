import datetime
from unittest import mock

from django.utils import timezone


current_timezone = timezone.get_current_timezone()

mock_now = mock.patch(
    "django.utils.timezone.now",
    mock.Mock(
        side_effect=lambda: datetime.datetime(2015, 10, 7, 14, 23, 0, tzinfo=current_timezone)
    ),
)

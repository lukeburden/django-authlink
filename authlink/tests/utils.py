import mock
import datetime
from django.utils import timezone

current_timezone = timezone.get_current_timezone()

mock_now = mock.patch('django.utils.timezone.now',
    mock.Mock(
        side_effect = lambda: current_timezone.localize(
            datetime.datetime(2015, 10, 0o7, 14, 23, 0)
        )
    )
)

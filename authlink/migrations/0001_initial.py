from django.conf import settings
from django.db import migrations, models

import authlink.utils


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="AuthLink",
            fields=[
                (
                    "key",
                    models.CharField(
                        default=authlink.utils.generate_authlink_key,
                        max_length=64,
                        serialize=False,
                        editable=False,
                        primary_key=True,
                    ),
                ),
                ("url", models.TextField()),
                ("ipaddress", models.GenericIPAddressField()),
                (
                    "created",
                    models.DateTimeField(default=authlink.utils.get_timezone_now),
                ),
                ("expires", models.DateTimeField()),
                ("used", models.DateTimeField(null=True, blank=True)),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
        )
    ]

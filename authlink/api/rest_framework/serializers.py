from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from ...adapter import get_adapter
from ...models import AuthLink


class AuthLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthLink
        fields = ("url",)

    def validate_url(self, value):
        if not get_adapter().in_url_whitelist(value):
            raise serializers.ValidationError(_("URL specified is not whitelisted"))
        return value

    def save(self, request):
        data = self.validated_data
        data["request"] = request._request
        return get_adapter().create(**data)

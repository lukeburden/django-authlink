from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from ...adapter import get_adapter
from .serializers import AuthLinkSerializer


class AuthLinkCreateView(CreateAPIView):
    """
    Authenticated view that takes a URL and creates a link for the current
    user that may be used to automatically establish a session on a related
    system.

    # Request #

        POST /v1/auth/link
        {
            "url": "/some/whitelisted/path?q=s"
        }

    # Response #

        HTTP 201 Created
        Content-Type: application/json
        Location: https://configurable/url/structure/auth/link/k6s1fhv3a6e99liamatxqrn1m6nynn1krbtzw47wxckhyiahwohp4f7bb8del6hf
        {
            "url": "/some/whitelisted/path?q=s"
        }

    # Server Configuration Hints #

    * whitelisted URLs must be provided in setting `AUTHLINK_URL_WHITELIST`.
    Default is an empty list.
    * you should set `AUTHLINK_URL_TEMPLATE` such that the `Location` header
    links directly to the authlink consumption endpoint. The template should
    contain `{key}`.
    """

    allowed_methods = ("POST",)
    serializer_class = AuthLinkSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        self.authlink = serializer.save(self.request)

    def get_success_headers(self, data):
        """Return the URL of our authenticated link."""
        return {"Location": get_adapter().get_full_url(self.authlink)}

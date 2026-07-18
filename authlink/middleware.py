from django.contrib.auth import BACKEND_SESSION_KEY
from django.core.exceptions import ImproperlyConfigured

from authlink.adapter import get_adapter


class AuthLinkWhitelistMiddleware:
    """
    Only allow access to whitelisted URLs for sessions that are
    established using the authlink authentication mechanism.

    Note: if you want the user to be able to access everything
    then don't use this middleware!
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, "session"):
            raise ImproperlyConfigured(
                "Please ensure you place AuthLinkWhitelistMiddleware "
                "middleware after your session middlware."
            )
        backend = request.session.get(BACKEND_SESSION_KEY)
        if backend and backend == "authlink.auth_backends.AuthLinkBackend":
            # resolve per request, like the views do, so AUTHLINK_ADAPTER_CLASS
            # changes and test overrides are honoured
            adapter = get_adapter()
            if not adapter.in_url_whitelist(request.path):
                return adapter.get_whitelist_failure_response(request)
        return self.get_response(request)

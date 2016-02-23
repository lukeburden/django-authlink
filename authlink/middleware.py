from authlink.adapter import get_adapter

from django.contrib.auth import BACKEND_SESSION_KEY


adapter = get_adapter()

class AuthLinkWhitelistMiddleware(object):
    """
    Only allow access to whitelisted URLs for sessions that are
    established using the authlink authentication mechanism.

    Note: if you want the user to be able to access everything
    then don't use this middleware!
    """
    def process_request(self, request):
        if not hasattr(request, 'session'):
            raise RuntimeError(
                'Please ensure you place AuthLinkWhitelistMiddleware ' \
                'middleware after the session middlware.'
            )
        backend = request.session.get(BACKEND_SESSION_KEY)
        if backend and backend == 'authlink.auth_backends.AuthLinkBackend':
            if not adapter.in_url_whitelist(request.path):
                return adapter.get_whitelist_failure_response(request)

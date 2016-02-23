from django.contrib.auth.backends import ModelBackend


class AuthLinkBackend(ModelBackend):
    """
    Placeholder authentication method effectively tagging a
    session as having been established using an authlink.
    """

    def authenticate(self, *args, **kwargs):
        return None

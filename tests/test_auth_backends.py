from django.contrib.auth import get_user_model
from django.test import TestCase

from authlink.auth_backends import AuthLinkBackend


class AuthLinkBackendTestCase(TestCase):
    """
    The backend exists purely to tag sessions established via an
    authlink; it must never be able to authenticate anyone itself.
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="luke", email="luke@...", password="top_secret"
        )
        self.backend = AuthLinkBackend()

    def test_authenticate_returns_none_without_credentials(self):
        self.assertIsNone(self.backend.authenticate(None))

    def test_authenticate_returns_none_even_with_valid_credentials(self):
        self.assertIsNone(self.backend.authenticate(None, username="luke", password="top_secret"))

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from rest_framework.test import APIClient


IP = "201.21.121.1"


@override_settings(
    MIDDLEWARE=settings.MIDDLEWARE + ("authlink.middleware.AuthLinkWhitelistMiddleware",),
    AUTHLINK_URL_WHITELIST=[r"^/authenticatedview/$"],
)
class AuthLinkEndToEndTestCase(TestCase):
    """
    Exercise the full documented flow: create a link via the API as an
    authenticated (password) user, then consume it in a fresh session
    that is confined to the whitelist.
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="luke", email="luke@...", password="top_secret"
        )

    def test_full_flow(self):
        api = APIClient()
        api.login(username="luke", password="top_secret")
        response = api.post(
            reverse("authlink_generate"),
            data={"url": "/authenticatedview/"},
            REMOTE_ADDR=IP,
        )
        self.assertEqual(response.status_code, 201)
        location = response["Location"]
        self.assertRegex(location, r"^/authlink/[a-z0-9]{64}$")

        # a fresh, unauthenticated session consumes the link
        webview = Client()
        response = webview.get(location, REMOTE_ADDR=IP)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/authenticatedview/")

        # the new session can access the whitelisted URL...
        response = webview.get("/authenticatedview/", REMOTE_ADDR=IP)
        self.assertEqual(response.status_code, 200)

        # ...but nothing outside the whitelist
        response = webview.get(reverse("authlink_generate"), REMOTE_ADDR=IP)
        self.assertEqual(response.status_code, 403)

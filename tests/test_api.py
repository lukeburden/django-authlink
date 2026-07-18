from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from rest_framework.test import APIClient

from authlink.models import AuthLink


@override_settings(AUTHLINK_URL_WHITELIST=[r"^/very/specific/url/$"])
class APITestCase(TestCase):
    """
    Ensure generation API is working properly.
    """

    def setUp(self):
        self.client = APIClient(format="json")
        self.user = get_user_model().objects.create_user(
            username="luke", email="luke@...", password="top_secret"
        )
        self.ipaddress = "201.21.121.1"

    def test_generate_ok_url(self):
        self.assertEqual(AuthLink.objects.count(), 0)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("authlink_generate"),
            data={"url": "/very/specific/url/"},
            REMOTE_ADDR=self.ipaddress,
        )
        self.assertEqual(response.status_code, 201)
        authlink = AuthLink.objects.all().first()
        self.assertEqual(authlink.user, self.user)
        self.assertEqual(authlink.ipaddress, self.ipaddress)
        self.assertEqual(AuthLink.objects.count(), 1)
        self.assertEqual(response["Location"], f"/authlink/{authlink.key}")

    @override_settings(AUTHLINK_URL_TEMPLATE="https://webapp.example.com/authlink/{key}")
    def test_generate_location_header_uses_template(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("authlink_generate"),
            data={"url": "/very/specific/url/"},
            REMOTE_ADDR=self.ipaddress,
        )
        self.assertEqual(response.status_code, 201)
        key = AuthLink.objects.get().key
        self.assertEqual(response["Location"], f"https://webapp.example.com/authlink/{key}")

    def test_generate_invalid_url(self):
        self.assertEqual(AuthLink.objects.count(), 0)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("authlink_generate"),
            data={"url": "/very/specific/but/wrong/url/"},
            REMOTE_ADDR=self.ipaddress,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(AuthLink.objects.count(), 0)

    def test_generate_not_authenticated(self):
        self.assertEqual(AuthLink.objects.count(), 0)
        response = self.client.post(
            reverse("authlink_generate"),
            data={"url": "/very/specific/url/"},
            REMOTE_ADDR=self.ipaddress,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(AuthLink.objects.count(), 0)

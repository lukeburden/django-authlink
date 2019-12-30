# -*- coding: utf-8 -*-


from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import SESSION_KEY
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from django.utils import timezone

from .utils import mock_now
from ..models import AuthLink

import datetime


TEST_URL = "/very/specific/url/"
NON_SUCCESS_URL = "http://testserver/"


@mock_now
class AuthLinkViewTestCase(TestCase):
    """
    We don't go crazy testing every case, just make sure our scenarios
    are hooked up and we get the expected errors.
    """

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="luke", email="luke@...", password="top_secret"
        )
        self.ipaddress = "201.021.121.1"
        now = timezone.now()
        self.authlink = AuthLink.objects.create(
            user=self.user,
            ipaddress=self.ipaddress,
            created=now,
            expires=now + datetime.timedelta(seconds=settings.AUTHLINK_TTL_SECONDS),
            url=TEST_URL,
        )

    def test_use_ok_not_authenticated(self):
        # the user should not be authenticated at this point
        self.assertNotIn(SESSION_KEY, self.client.session)
        response = self.client.get(
            reverse("authlink_use", kwargs={"key": self.authlink.key}),
            REMOTE_ADDR=self.ipaddress,
        )
        self.assertEqual(response.status_code, 301)
        self.assertIn(TEST_URL, response.get("Location"))
        self.authlink = AuthLink.objects.get(pk=self.authlink.pk)
        self.assertTrue(self.authlink.used)
        # the user should be authenticated at this point
        self.assertEqual(int(self.client.session[SESSION_KEY]), self.user.pk)

    def test_use_ok_already_authenticated_same_user(self):
        self.client.login(username="luke", password="top_secret")
        # the user should not be authenticated at this point
        self.assertEqual(int(self.client.session[SESSION_KEY]), self.user.pk)
        response = self.client.get(
            reverse("authlink_use", kwargs={"key": self.authlink.key}),
            REMOTE_ADDR=self.ipaddress,
        )
        self.assertEqual(response.status_code, 301)
        self.assertIn(TEST_URL, response.get("Location"))
        # the same user should be authenticated at this point
        self.assertEqual(int(self.client.session[SESSION_KEY]), self.user.pk)

    def test_use_ok_already_authenticated_different_user(self):
        another_user = get_user_model().objects.create_user(
            username="another", email="another@...", password="top_secret"
        )
        self.client.login(username=another_user.username, password="top_secret")
        self.assertEqual(int(self.client.session[SESSION_KEY]), another_user.pk)
        # the user should not be authenticated at this point
        response = self.client.get(
            reverse("authlink_use", kwargs={"key": self.authlink.key}),
            REMOTE_ADDR=self.ipaddress,
        )
        self.assertEqual(response.status_code, 301)
        self.assertIn(TEST_URL, response.get("Location"))
        self.assertEqual(int(self.client.session[SESSION_KEY]), self.authlink.user.pk)

    def test_use_expired(self):
        self.authlink.expires = timezone.now()
        self.authlink.save()
        response = self.client.get(
            reverse("authlink_use", kwargs={"key": self.authlink.key}),
            REMOTE_ADDR=self.ipaddress,
        )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(NON_SUCCESS_URL, response.get("Location"))
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.authlink = AuthLink.objects.get(pk=self.authlink.pk)
        self.assertFalse(self.authlink.used)

    def test_use_used(self):
        self.authlink.used = timezone.now()
        self.authlink.save()
        response = self.client.get(
            reverse("authlink_use", kwargs={"key": self.authlink.key}),
            REMOTE_ADDR=self.ipaddress,
        )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(NON_SUCCESS_URL, response.get("Location"))
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_use_mismatched_ipaddresses(self):
        response = self.client.get(
            reverse("authlink_use", kwargs={"key": self.authlink.key}),
            REMOTE_ADDR="201.021.121.2",
        )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(NON_SUCCESS_URL, response.get("Location"))
        self.assertNotIn(SESSION_KEY, self.client.session)

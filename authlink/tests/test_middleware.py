# -*- coding: utf-8 -*-


from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import SESSION_KEY
from django.contrib.auth import BACKEND_SESSION_KEY
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from django.test.utils import override_settings
from django.utils import timezone

from .utils import mock_now
from ..models import AuthLink

import datetime


TEST_URL = '/very/specific/url/'
NON_SUCCESS_URL = 'http://testserver/'

@mock_now
class AuthLinkMiddlewareTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='luke', email='luke@...', password='top_secret'
        )
        self.ipaddress = '201.021.121.1'
        now = timezone.now()
        self.authlink = AuthLink.objects.create(
            user = self.user,
            ipaddress = self.ipaddress,
            created = now,
            expires = now + datetime.timedelta(seconds=settings.AUTHLINK_TTL_SECONDS),
            url = TEST_URL
        )

    def test_middleware_not_active(self):
        """
        No URLs are whitelisted, but the middleware isn't active
        """
        self.assertNotIn(SESSION_KEY, self.client.session)
        response = self.client.get(
            reverse('authlink_use', kwargs={'key': self.authlink.key}),
            REMOTE_ADDR = self.ipaddress
        )
        self.assertEqual(response.status_code, 301)
        response = self.client.get(
            reverse('authenticated_view')
        )
        self.assertEqual(response.status_code, 200)


    @override_settings(
        MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES + (
            'authlink.middleware.AuthLinkWhitelistMiddleware',
        ),
        AUTHLINK_URL_WHITELIST=(r'/authenticatedview/',)
    )
    def test_middleware_active_url_whitelisted(self):
        # the user should not be authenticated at this point
        self.assertNotIn(SESSION_KEY, self.client.session)
        response = self.client.get(
            reverse('authlink_use', kwargs={'key': self.authlink.key}),
            REMOTE_ADDR = self.ipaddress
        )
        self.assertEqual(response.status_code, 301)
        response = self.client.get(
            reverse('authenticated_view')
        )
        self.assertEqual(response.status_code, 200)

    
    @override_settings(
        MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES + (
            'authlink.middleware.AuthLinkWhitelistMiddleware',
        ),
        AUTHLINK_URL_WHITELIST=[]
    )
    def test_middleware_active_url_not_whitelisted(self):
        # the user should not be authenticated at this point
        self.assertNotIn(SESSION_KEY, self.client.session)
        response = self.client.get(
            reverse('authlink_use', kwargs={'key': self.authlink.key}),
            REMOTE_ADDR = self.ipaddress
        )
        self.assertEqual(response.status_code, 301)
        response = self.client.get(
            reverse('authenticated_view')
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.content,
            'That URL is not whitelisted for your authentication method.'
        )


    @override_settings(
        MIDDLEWARE_CLASSES = (
            'authlink.middleware.AuthLinkWhitelistMiddleware',
        ),
    )
    def test_middleware_after_session_middleware(self):
        with self.assertRaises(ImproperlyConfigured) as ic:
            response = self.client.get(
                reverse('authlink_use', kwargs={'key': self.authlink.key}),
                REMOTE_ADDR = self.ipaddress
            )
            self.assertEqual(response.status_code, 500)
            self.assertEqual(
                ic.exception.message,
                'ImproperlyConfigured: Please ensure you place AuthLinkWhitelistMiddleware middleware after your session middlware.'
            )


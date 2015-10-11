# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
from django.test import RequestFactory
from django.test.utils import override_settings
from django.utils import timezone
from authlink.adapter import get_adapter
from authlink.adapter import DefaultAuthLinkAdapter
from authlink.models import AuthLink
from authlink.tests.utils import mock_now

import datetime
from importlib import import_module


class TestAdapter(DefaultAuthLinkAdapter):
    pass

class AdapterTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='luke', email='luke@...', password='top_secret'
        )
        self.factory = RequestFactory()
        self.adapter = get_adapter()
        now = timezone.now()
        self.authlink = AuthLink.objects.create(
            user = self.user,
            ipaddress = '177.139.233.133',
            created = now,
            expires = now + datetime.timedelta(seconds=settings.AUTHLINK_TTL_SECONDS),
            url = '/some/url'
        )

    def test_get_adapter(self):
        self.assertEqual(DefaultAuthLinkAdapter, self.adapter.__class__)

    @override_settings(
        AUTHLINK_ADAPTER_CLASS = 'authlink.tests.test_adapter.TestAdapter'
    )
    def test_get_adapter_configurable(self):
        adapter = get_adapter()
        self.assertEqual(TestAdapter, adapter.__class__)

    def test_create_ok(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        request.META = {
            'REMOTE_ADDR': '177.139.233.133'
        }
        self.assertTrue(request.user.is_authenticated())
        authlink = self.adapter.create(**{'url': '/some/url', 'request': request})
        self.assertEqual(authlink.ipaddress, '177.139.233.133')
        self.assertEqual(authlink.user, self.user)
        self.assertEqual(
            authlink.expires,
            authlink.created + datetime.timedelta(seconds=settings.AUTHLINK_TTL_SECONDS)
        )

    def test_create_ipaddress_missing(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        with self.assertRaises(IntegrityError):
            authlink = self.adapter.create(
                **{'url': '/some/url', 'request': request}
            )

    def test_create_user_not_authenticated(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        request.user.is_authenticated = lambda: False
        request.META = {
            'REMOTE_ADDR': '177.139.233.133'
        }
        with self.assertRaises(RuntimeError):
            authlink = self.adapter.create(
                **{'url': '/some/url', 'request': request}
            )
    
    def test_calculate_expiry(self):
        now = timezone.now()
        expires = self.adapter.calculate_expiry(now)
        self.assertEqual(expires, now + datetime.timedelta(seconds=settings.AUTHLINK_TTL_SECONDS))

    @override_settings(
        AUTHLINK_TTL_SECONDS = 62
    )
    @mock_now
    def test_calculate_expiry_configurable(self):
        now = timezone.now()
        expires = self.adapter.calculate_expiry(now)
        self.assertEqual(expires, now + datetime.timedelta(seconds=62))


    def test_extract_ipaddress(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        request.META = {
            'REMOTE_ADDR': '177.139.233.133'
        }
        self.assertEqual(
            self.adapter.extract_ipaddress(request),
            '177.139.233.133'
        )

    def test_extract_ipaddress_non_debug_localhost(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        request.META = {
            'REMOTE_ADDR': '127.0.0.1'
        }
        self.assertEqual(
            self.adapter.extract_ipaddress(request),
            None
        )

    @override_settings(
        DEBUG = True
    )
    def test_extract_ipaddress_debug_localhost(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        request.META = {
            'REMOTE_ADDR': '127.0.0.1'
        }
        self.assertEqual(
            self.adapter.extract_ipaddress(request),
            '127.0.0.1'
        )

    # def test_add_message(self):
    #     #def test_add_message(self, request, level, message):
    #     pass

    # def test_error(self):
    #     #test_error(self, request, message)
    #     pass

    def test_login(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore()
        self.adapter.login(request, self.authlink)
        self.assertIn('_auth_user_id', request.session.keys())

    def test_logout(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore()
        self.adapter.logout(request)
        self.assertNotIn('_auth_user_id', request.session.keys())

    def test_use(self):
        self.assertFalse(self.authlink.used)
        self.adapter.use(self.authlink)
        self.assertTrue(self.authlink.used)

    @mock_now
    def test_is_expired_false(self):
        now = timezone.now()
        self.authlink.expires = now + datetime.timedelta(seconds=1)
        self.assertFalse(self.adapter.is_expired(self.authlink))

    @mock_now
    def test_is_expired_exact(self):
        now = timezone.now()
        self.authlink.expires = now
        self.assertTrue(self.adapter.is_expired(self.authlink))

    @mock_now
    def test_is_expired_true(self):
        now = timezone.now()
        self.authlink.expires = now - datetime.timedelta(seconds=1)
        self.assertTrue(self.adapter.is_expired(self.authlink))

    def test_is_used(self):
        self.assertFalse(self.adapter.is_used(self.authlink))
        self.adapter.use(self.authlink)
        self.assertTrue(self.adapter.is_used(self.authlink))

    def test_ipaddress_matches_cannot_extract(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        self.assertFalse(self.adapter.ipaddress_matches(request, self.authlink))

    def test_ipaddress_matches_different(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        request.META = {
            'REMOTE_ADDR': '177.139.233.134'
        }
        self.assertFalse(self.adapter.ipaddress_matches(request, self.authlink))

    def test_ipaddress_matches_ok(self):
        request = self.factory.get('/some/url')
        request.user = self.user
        request.META = {
            'REMOTE_ADDR': '177.139.233.133'
        }
        self.assertTrue(self.adapter.ipaddress_matches(request, self.authlink))

    def test_get_full_url(self):
        # produces an url with embedded key
        self.assertIn(
            self.authlink.key,
            self.adapter.get_full_url(self.authlink)
        )

    @override_settings(AUTHLINK_URL_TEMPLATE='/some/url/{key}')
    def test_get_full_url_configurable(self):
        self.assertIn(
            '/some/url/%s' % self.authlink.key,
            self.adapter.get_full_url(self.authlink)
        )

    def test_in_url_whitelist_default_deny(self):
        self.assertFalse(
            self.adapter.in_url_whitelist('/nothing/will/work')
        )
    
    @override_settings(AUTHLINK_URL_WHITELIST=[r'^/very/specific/url/$'])
    def test_in_url_whitelist_not_in(self):
        self.assertFalse(
            self.adapter.in_url_whitelist('/whatever/should/work')
        )

    @override_settings(AUTHLINK_URL_WHITELIST=[r'^/very/specific/url/$'])
    def test_in_url_whitelist_in(self):
        self.assertTrue(
            self.adapter.in_url_whitelist('/very/specific/url/')
        )

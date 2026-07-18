import string

from django.test import TestCase
from django.test.utils import override_settings

from authlink.utils import generate_authlink_key


class GenerateAuthLinkKeyTestCase(TestCase):
    def test_default_length_and_charset(self):
        key = generate_authlink_key()
        self.assertEqual(len(key), 64)
        self.assertTrue(set(key) <= set(string.ascii_lowercase + string.digits))

    @override_settings(AUTHLINK_KEY_LENGTH=32)
    def test_length_configurable(self):
        self.assertEqual(len(generate_authlink_key()), 32)

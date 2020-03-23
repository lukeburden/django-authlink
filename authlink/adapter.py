import datetime
import importlib
import ipaddress
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ipware.ip import get_ip, get_real_ip

from .models import AuthLink


class DefaultAuthLinkAdapter(object):
    """
    Most application logic should live here, such that it becomes
    easily overridable.
    """

    def create(self, **kwargs):
        request = kwargs.pop("request")
        if not request.user.is_authenticated:
            raise RuntimeError(
                "User not authenticated, cannot create AuthLink. Check for this in view."
            )
        authlink = AuthLink(**kwargs)
        authlink.user = request.user
        authlink.ipaddress = self.extract_ipaddress(request)
        authlink.expires = self.calculate_expiry(authlink.created)
        authlink.save()
        return authlink

    def calculate_expiry(self, created):
        return created + datetime.timedelta(
            seconds=getattr(settings, "AUTHLINK_TTL_SECONDS", 60)
        )

    def extract_ipaddress(self, request):
        ipaddress = get_real_ip(request)
        if not ipaddress and settings.DEBUG:
            ipaddress = get_ip(request)
        return ipaddress

    def add_message(self, request, level, message):
        messages.add_message(request, level, message)

    def info(self, request, message):
        self.add_message(request, messages.INFO, message)

    def error(self, request, message):
        self.add_message(request, messages.ERROR, message)

    def login(self, request, authlink):
        """
        Mark the user session as having use AuthLinkBackend
        such that future requests can act on this information.
        """
        user = authlink.user
        user.backend = "authlink.auth_backends.AuthLinkBackend"
        login(request, user)

    def logout(self, request):
        logout(request)

    def use(self, authlink):
        authlink.used = timezone.now()
        authlink.save()

    def is_expired(self, authlink):
        return authlink.expires <= timezone.now()

    def is_used(self, authlink):
        return authlink.used

    def ipaddress_matches(self, request, authlink):
        # leverage python standard lib to properly compare the two addresses as
        # string comparison can be unreliable
        request_ip = self.extract_ipaddress(request)
        request_ip = ipaddress.ip_address(request_ip) if request_ip else request_ip
        expected_ip = ipaddress.ip_address(authlink.ipaddress)
        return request_ip == expected_ip

    def get_full_url(self, authlink):
        return getattr(settings, "AUTHLINK_URL_TEMPLATE", "/authlink/{key}").format(
            key=authlink.key
        )

    def in_url_whitelist(self, url):
        whitelist = getattr(settings, "AUTHLINK_URL_WHITELIST", [])
        for url_re in whitelist:
            if re.match(url_re, url):
                return True
        return False

    def get_whitelist_failure_response(self, request):
        return HttpResponseForbidden(
            _("That URL is not whitelisted for your " "authentication method.")
        )


def get_adapter():
    class_path = getattr(settings, "AUTHLINK_ADAPTER_CLASS", None)
    if class_path:
        pkg, attr = class_path.rsplit(".", 1)
        return getattr(importlib.import_module(pkg), attr)()
    return DefaultAuthLinkAdapter()

from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from .adapter import get_adapter
from .models import AuthLink


class AuthLinkView(View):
    """
    An endpoint that can be used to consume an
    authenticated link.
    """

    @transaction.atomic
    def get(self, request, key):
        authlink = get_object_or_404(AuthLink, key=key)
        adapter = get_adapter()
        if adapter.is_expired(authlink):
            return self.on_expired(request, authlink)

        if adapter.is_used(authlink):
            return self.on_used(request, authlink)

        if not adapter.ipaddress_matches(request, authlink):
            return self.on_address_mismatch(request, authlink)

        if request.user.is_authenticated:
            if request.user != authlink.user:
                adapter.logout(request)

        adapter.use(authlink)
        adapter.login(request, authlink)
        return self.on_success(request, authlink)

    def on_expired(self, request, authlink):
        get_adapter().error(request, _("Link has expired."))
        return self.on_non_success(request, authlink)

    def on_used(self, request, authlink):
        get_adapter().error(request, _("Link has already been used."))
        return self.on_non_success(request, authlink)

    def on_address_mismatch(self, request, authlink):
        get_adapter().error(
            request,
            _("Mismatch between generation IP address and consumption IP address."),
        )
        return self.on_non_success(request, authlink)

    def on_non_success(self, request, authlink):
        return HttpResponseRedirect(
            getattr(settings, "AUTHLINK_NON_SUCCESS_REDIRECT_URL", "/"), status=301
        )

    def on_success(self, request, authlink):
        return HttpResponseRedirect(authlink.url, status=301)

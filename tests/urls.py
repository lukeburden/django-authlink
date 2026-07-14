from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import re_path
from django.views.generic import View

from authlink.api.rest_framework.views import AuthLinkCreateView
from authlink.views import AuthLinkView


class AuthenticatedView(View):
    """
    Simple view to use in tests
    """

    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello, World!")


urlpatterns = [
    re_path(r"^api/authlink/$", AuthLinkCreateView.as_view(), name="authlink_generate"),
    re_path(r"^authlink/(?P<key>[\w]+)$", AuthLinkView.as_view(), name="authlink_use"),
    re_path(
        r"^authenticatedview/$",
        login_required(AuthenticatedView.as_view()),
        name="authenticated_view",
    ),
]

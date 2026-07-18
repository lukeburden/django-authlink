# Django Authlink

[![](https://img.shields.io/pypi/v/django-authlink.svg)](https://pypi.python.org/pypi/django-authlink/)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://pypi.python.org/pypi/django-authlink/)
[![Test](https://github.com/lukeburden/django-authlink/actions/workflows/test.yml/badge.svg)](https://github.com/lukeburden/django-authlink/actions/workflows/test.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


## django-authlink

`django-authlink` is a Django app that faciliates authentication using magic links. This is perfect for allowing a mobile-app to authenticate for webviews, but could be used for myriad other cases where you need to pre-authenticate the user.

Convenient APIs for Django Rest Framework are included.

### Installation ####

```shell
pip install django-authlink
```

Add `authlink` to your INSTALLED_APPS setting and then expose `authlink.api.rest_framework.views.AuthLinkCreateView` in your API, and `authlink.views.AuthLinkView` in your web application.

The exact URLs you use is up to you, but here is an example:

```python
from django.contrib import admin
from django.urls import path

from authlink.views import AuthLinkView
from authlink.api.rest_framework.views import AuthLinkCreateView

urlpatterns = [
    path('api/authlink', AuthLinkCreateView.as_view()),
    path(r'authlink/(?P<key>[\w]+)$', AuthLinkView.as_view()),
]
```

Now you should set `AUTHLINK_URL_TEMPLATE` to match the URL structure in your web application:

```python
AUTHLINK_URL_TEMPLATE = "/authlink/{key}"
```

This will allow the API to build the correct location for mobile apps to load into web views.

### Usage ###

When your mobile app needs to load an authenticated webview, it should hit the API to get an authlink:


```http
POST /api/authlink
{
    "url": "/some/whitelisted/path/in/your/webapp"
}
```

Assuming the user was currently authenticated, this will return:

```http
HTTP 201 Created
Content-Type: application/json
Location: https://authlink/k6s1fhv3a6e99liamatxqrn1m6nynn1krbtzw47wxckhyiahwohp4f7bb8del6hf
{
    "url": "/some/whitelisted/path/in/your/webapp"
}
```

To load the authenticated webview, your mobile app can now open its particular webview class using the `Location` in the response above, and if the token is valid the target URL will load authenticated.

### Security ###
When you share an authlink, you are essentially providing unfettered authenticated access to a user's account. `django-authlink` attempts to reduce the chances of having one of these links somehow fall into the hands of an attacker and give them access to another user's account using several measures.

1. A tight expiry window; by default authlinks are only valid for 60 seconds. You can reduce this to further close the window of validity and so vulnerability.
2. Whitelisting of URLs; you need to specify what web-app URLs you want to allow authlinks to be created for. Note that once the user is authenticated, they can browse around, so this is not going to actually limit them to that URL.
3. Matching of IP addresses; the IP address used when creating the authlink via the API must match the IP address of the request to use the authlink in the web application.

Depsite these measures, there is still an undeniable security risk to using this authentication method. You need to weigh the pros and cons for your particular use case and make your own decision there whether this makes sense for your project.

Note that IP addresses are extracted using [django-ipware](https://github.com/un33k/django-ipware), which by default inspects proxy headers such as `X-Forwarded-For` — headers that clients can trivially forge. For the IP matching measure to be meaningful, your reverse proxy or load balancer must strip or overwrite these headers on incoming requests. Alternatively, override `extract_ipaddress()` on a custom adapter and pass ipware's trusted proxy options (`proxy_count`, `proxy_trusted_ips`) or set `IPWARE_META_PRECEDENCE_ORDER` to match your infrastructure.


### Configuration ###

#### AUTHLINK_URL_TEMPLATE ####
Default: "/authlink/{key}"

Allows variation of the redirect URLs that the authlink create API produces.

#### AUTHLINK_URL_WHITELIST ####
Default: []

A list of URL names that you want to restrict authlinks being created for.

#### AUTHLINK_ADAPTER_CLASS ####
Default: "authlink.adapter.DefaultAuthLinkAdapter"

You can subclass the adapter and add any customisations you want to general authlink behaviour.

#### AUTHLINK_TTL_SECONDS ####
Default: 60

Allows increasing or decreasing the period of validity for an authlink.

#### AUTHLINK_NON_SUCCESS_REDIRECT_URL ####
Default: "/"

Where the user is redirected when consuming an authlink fails (expired, already used,
or IP address mismatch).

#### AUTHLINK_KEY_LENGTH ####
Default: 64

Length of generated authlink keys. Note that the shipped migration creates the key
column as `varchar(64)`, so values above 64 require adding a migration in your own
project; values at or below 64 work as-is.


### Supported versions

`django-authlink` supports the Python and Django versions currently supported upstream:

- Python 3.10 through 3.14
- Django 5.2 (LTS) and 6.0

Django's `main` branch is also tested in CI, but failures there do not fail the build.

### Contribute

Tests run via [tox](https://tox.wiki) across all supported Python/Django combinations, and
[GitHub Actions](https://github.com/lukeburden/django-authlink/actions) runs the same
environments on push and pull request.

To run the tests locally against the Python versions you have installed:

```bash
pip install tox
tox
```

To run a single environment, or lint/format checks with [Ruff](https://docs.astral.sh/ruff/):

```bash
tox -e py313-dj60
tox -e ruff
```

Releases are published to PyPI automatically when a GitHub release is created.

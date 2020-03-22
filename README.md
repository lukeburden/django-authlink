# Django Authlink

[![](https://img.shields.io/pypi/v/django-authlink.svg)](https://pypi.python.org/pypi/django-authlink/)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://pypi.python.org/pypi/django-authlink/)
[![CircleCI](https://circleci.com/gh/lukeburden/django-authlink.svg?style=svg)](https://circleci.com/gh/lukeburden/django-authlink)
[![Codecov](https://codecov.io/gh/lukeburden/django-authlink/branch/master/graph/badge.svg)](https://codecov.io/gh/lukeburden/django-authlink)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


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


### Contribute

`django-authlink` supports a variety of Python and Django versions. It's best if you test each one of these before committing. Our [Circle CI Integration](https://circleci.com) will test these when you push but knowing before you commit prevents from having to do a lot of extra commits to get the build to pass.

#### Environment Setup

In order to easily test on all these Pythons and run the exact same thing that CI will execute you'll want to setup [pyenv](https://github.com/yyuu/pyenv) and install the Python versions outlined in [tox.ini](tox.ini).

If you are on Mac OS X, it's recommended you use [brew](http://brew.sh/). After installing `brew` run:

```bash
brew install pyenv pyenv-virtualenv pyenv-virtualenvwrapper
```

Next, install the various python versions we want to test against and create a virtualenv specifically for `django-authlink`:

```bash
pyenv install 3.6.10
pyenv install 3.7.6
pyenv install 3.8.1
pyenv virtualenv 3.8.1 authlink
pyenv activate authlink
pip install detox
pyenv shell authlink 3.6.10 3.7.6
```

Now ensure the `authlink` virtualenv is activated, make the other python versions also on our path, and run the tests!


```bash
pyenv shell authlink 3.6.10 3.7.6
detox
```

This will execute the test environments in parallel as defined in the `tox.ini`.

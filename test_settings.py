# -*- coding: utf-8 -*-

import django

SECRET_KEY = "sosecreteh"
SITE_ID = 1

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "authlink",
)

ROOT_URLCONF = "test_urls"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "authlink.auth_backends.AuthLinkBackend",
)

STATIC_ROOT = "/tmp/"  # Dummy
STATIC_URL = "/static/"

AUTHLINK_TTL_SECONDS = 60

TIME_ZONE = "UTC"
USE_TZ = True

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

#!/usr/bin/env python

from distutils.core import setup

CLASSIFIERS = [
	"Development Status :: 4 - Beta",
        "Environment :: Web Environment",
	"Framework :: Django",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: MIT License",
	"Programming Language :: Python",
	"Programming Language :: Python :: 2.7",
	"Topic :: Software Development :: Libraries :: Python Modules",
	"Topic :: System :: Networking",
]

setup(
	name="django-authlink",
	packages=[
		"authlink",
		"authlink/api",
		"authlink/api/rest_framework",
		"authlink/migrations",
	],
	author="Luke Burden",
	author_email="lukeburden@gmail.com",
	classifiers=CLASSIFIERS,
	description="Generate pre-authenticated expiring links via a Django based API to be used in a Django web application.",
	download_url="https://github.com/lukeburden/django-authlink/tarball/master",
	long_description="""Occasionally there will be a need to redirect an API/Mobile App user to a web application in order to access some functionality that is not yet supported in the API/Mobile app. In this instance if the user has already authenticated against the API, it is desirable to have them automatically be authenticated when accessing the web application.

This utility library allows an API user to generate short-lived, pre-authenticated links for a restricted set of URLs. When these are consumed, if various security checks are satisfied the user is automatically logged in and redirected to the pre-authenticated URL.""",
	url="https://github.com/lukeburden/django-authlink",
	version="0.0.1",
)

# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, include, url

from authlink.api.rest_framework.views import AuthLinkCreateView
from authlink.views import AuthLinkView


urlpatterns = patterns('',
    url(r'^api/authlink/$', AuthLinkCreateView.as_view(), name='authlink_generate'),
    url(r'^authlink/(?P<key>[\w]+)$', AuthLinkView.as_view(), name='authlink_use')
)
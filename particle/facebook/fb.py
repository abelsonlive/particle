#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import facepy
import yaml
from datetime import datetime, timedelta
from urlparse import parse_qs
from particle.common import DEBUG
import logging

def connect(config):
    return facepy.GraphAPI(config['facebook']['stable_access_token'])

def generate_extended_access_token(config):
    """
    Get an extended OAuth access token.

    :param access_token: A string describing an OAuth access token.
    :param application_id: An integer describing the Facebook application's ID.
    :param application_secret_key: A string describing the Facebook application's secret key.

    Returns a tuple with a string describing the extended access token and a datetime instance
    describing when it expires.
    """
    tests = [
        not config['facebook'].has_key('stable_access_token'),
        config['facebook']['stable_access_token'] is None

    ]
    if any(tests):
        # access tokens
        default_access_token = facepy.get_application_access_token(
            application_id = config['facebook']['app_id'],  
            application_secret_key = config['facebook']['app_secret']
        )
        graph = facepy.GraphAPI(default_access_token)

        response = graph.get(
            path='oauth/access_token',
            client_id = config['facebook']['app_id'],
            client_secret = config['facebook']['app_secret'],
            grant_type = 'fb_exchange_token',
            fb_exchange_token = config['facebook']['temp_access_token']
        )

        components = parse_qs(response)

        token = components['access_token'][0]
        expires_at = datetime.now() + timedelta(seconds=int(components['expires'][0]))

        config['facebook'].pop('stable_access_token', token)
        config['facebook'].pop('stable_access_token_expires_at', int(expires_at.strftime("%s")))
        print "INFO: This is your new stable facebook access token: %s" % token
        print "INFO: It will expire on %s" % expires_at.strftime("%Y-%m-%d")
        return config

    else:
        return config

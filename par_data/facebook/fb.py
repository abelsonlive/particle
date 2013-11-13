#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import facepy
import yaml
from datetime import datetime, timedelta
from urlparse import parse_qs
from par_data.common import DEBUG, CONFIG

def generate_extended_access_token():
    """
    Get an extended OAuth access token.

    :param access_token: A string describing an OAuth access token.
    :param application_id: An integer describing the Facebook application's ID.
    :param application_secret_key: A string describing the Facebook application's secret key.

    Returns a tuple with a string describing the extended access token and a datetime instance
    describing when it expires.
    """

    # access tokens
    default_access_token = facepy.get_application_access_token(
        application_id = CONFIG['facebook']['app_id'],  
        application_secret_key = CONFIG['facebook']['app_secret']
    )
    graph = facepy.GraphAPI(default_access_token)

    response = graph.get(
        path='oauth/access_token',
        client_id = CONFIG['facebook']['app_id'],
        client_secret = CONFIG['facebook']['app_secret'],
        grant_type = 'fb_exchange_token',
        fb_exchange_token = CONFIG['facebook']['temp_access_token']
    )

    components = parse_qs(response)

    token = components['access_token'][0]
    expires_at = datetime.now() + timedelta(seconds=int(components['expires'][0]))

    if not CONFIG['facebook'].has_key('stable_access_token'):
        CONFIG['facebook'].pop('stable_access_token', token)
        CONFIG['facebook'].pop('stable_access_token_expires_at', int(expires_at.strftime("%s")))
        
        with open(os.getenv('PARDATA_CONFIG_PATH'), 'wb') as f:
            f.write(yaml.dump(CONFIG, default_flow_style=False))
            print "INFO: THIS IS YOUR STABLE ACCESS TOKEN: %s" % token
            print "INFO: IT EXPIRES AT %s" % expires_at
            print "INFO: YOUR CONFIG FILE (%s) HAS BEEN UPDATED" % '../par_data.yml'

def connect():
    return facepy.GraphAPI(CONFIG['facebook']['stable_access_token'])

if __name__ == '__main__':
    generate_extended_access_token()
    

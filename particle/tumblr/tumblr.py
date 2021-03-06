#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytumblr
import logging

def connect(config):
  return pytumblr.TumblrRestClient(
    config['tumblr']['consumer_key'], 
    config['tumblr']['consumer_secret'], 
    config['tumblr']['oauth_token'], 
    config['tumblr']['oauth_token_secret']
  )

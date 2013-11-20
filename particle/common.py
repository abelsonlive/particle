#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import yaml

# GLOBAL settings
DEBUG = False
APP_DEBUG = True

# initialize redis
db = redis.StrictRedis(host='localhost', port=6379, db=0)

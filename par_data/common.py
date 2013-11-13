#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import redis
import yaml

# defaults
PRINT_OUTPUT = False
DEBUG = False
APP_DEBUG = True
INIT = False

# initialize redis
db = redis.StrictRedis(host='localhost', port=6379, db=0)

try:
  # load config
  CONFIG = yaml.safe_load(open(os.getenv('PARDATA_CONFIG_PATH')))
except Exception as e:
  print("WARNING YOU MUST SET $PARDATA_CONFIG_PATH with a valid pardata.yml file")
  print e
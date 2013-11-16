#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import redis
import yaml

# defaults
DEBUG = False
APP_DEBUG = True

# initialize redis
db = redis.StrictRedis(host='localhost', port=6379, db=0)

try:
  # load config
  CONFIG = yaml.safe_load(open(os.getenv('PARTICLE_CONFIG_PATH')))
except Exception as e:
  print "YOU MUST SET $PARTICLE_CONFIG_PATH with a valid particle.yml filepath"
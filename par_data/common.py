#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

import redis
import yaml

# defaults
PRINT_OUTPUT = False
DEBUG = False
APP_DEBUG = True
INIT = False

# initialize redis
db = redis.StrictRedis(host='localhost', port=6379, db=0)

# load config
CONFIG = yaml.safe_load(open('../par_data.yml'))



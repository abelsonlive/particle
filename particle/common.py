#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dataset

# GLOBAL settings
DEBUG = False

# initialize redis
db = dataset.connect('postgresql://brian:particle@localhost:5432/particle')

urls_table = db['urls']
fb_table = db['facebook']
ins_table = db['insights']
twt_table = db['twitter']
pp_table = db['promopages']
rss_table = db['rssfeeds']

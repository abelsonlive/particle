#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from thready import threaded
from par_data.facebook import internal_facebook
from par_data.twitter import internal_twitter
from par_data.promopages import promopages
from par_data.rssfeeds import rssfeeds
from par_data.facebook import fb
from par_data.twitter import twt
from par_data.common import DEBUG, db, INIT
import json

def init():
  # fb.generate_extended_access_token()
  twt.generate_list()
  db.sadd('twitter_twt_ids', None)
  db.sadd('facebook_post_ids', None)
  db.sadd('article_set', None)
  db.zadd('article_sorted_set', 0, json.dumps(dict(url=None)))

def execute(task):
  task.run()

def run():
  tasks = [
    # rssfeeds,
    internal_facebook
    # internal_twitter,
    # promopages
  ]
  print("\n\n")
  for task in tasks:
    execute(task)


if __name__ == '__main__':
  run()


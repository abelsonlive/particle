#!/usr/bin/python
# -*- coding: utf-8 -*-

from thready import threaded
import json, yaml
from optparse import OptionParser

from par_data.facebook import facebook
from par_data.twitter import twitter
from par_data.promopages import promopages
from par_data.rssfeeds import rssfeeds
from par_data.facebook import fb
from par_data.twitter import twt
from par_data.common import DEBUG, db, INIT

def init():
  fb.generate_extended_access_token()
  twt.generate_list()
  db.sadd('twitter_twt_ids', None)
  db.sadd('facebook_post_ids', None)
  db.sadd('article_set', None)
  db.zadd('article_sorted_set', 0, json.dumps(dict(url=None)))

def execute(task):
  task.run()

def run():
  tasks = [
    promopages,
    rssfeeds,
    twitter,
    facebook
  ]
  print("\n\n")
  if DEBUG:
    for task in tasks:
      execute(task)
  else:
    threaded(tasks, execute, 2, 4)


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-i", "--init", dest="init", default="false")
  opts, args = parser.parse_args()
  if opts.init =='true':
    init()
  else:
    run()


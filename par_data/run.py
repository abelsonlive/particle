#!/usr/bin/python
# -*- coding: utf-8 -*-

from thready import threaded
import json, yaml, os
from optparse import OptionParser

from par_data.facebook import facebook
from par_data.twitter import twitter
from par_data.promopages import promopages
from par_data.rssfeeds import rssfeeds
from par_data.facebook import fb
from par_data.twitter import twt
from par_data.common import DEBUG, db, INIT

def config(filepath, config=None):
  cwd = os.getcwd()
  filepath = os.path.join(cwd, filepath.split("/")[-1])
  # initialize config file
  if config is None:
    if filepath.endswith('.yml'):
      format ='yaml'
      c = yaml.safe_load(open(filepath))
    elif filepah.endswith('.json'):
      format = 'json'
      c = yaml.safe_load(open(filepath))
  elif isinstance(config, dict):
      format = 'yaml'
      c = config
  print filepath
  # set environmental variable
  os.environ['PARDATA_CONFIG_PATH'] = filepath

  # write to file:
  with open(filepath, 'wb') as f:
    if format == 'yaml':
      f.write(yaml.dump(c, indent =2, default_flow_style=False))
    elif format == 'json':
      f.write(json.dumps(c, indent = 2, sort_keys=False))

  fb.generate_extended_access_token()
  twt.generate_list()

def execute(task):
  task.run()

def run():
  tasks = [
    promopages,
    rssfeeds,
    twitter,
    facebook
  ]
  print("\n----------------------------------\n")
  if DEBUG:
    for task in tasks:
      execute(task)
  else:
    threaded(tasks, execute, 2, 4)


if __name__ == '__main__':
    import sys
    try:
      config(sys.argv[1])
    except:
      run()


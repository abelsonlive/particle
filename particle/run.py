#!/usr/bin/python
# -*- coding: utf-8 -*-

from thready import threaded
import json, yaml, os
from optparse import OptionParser

from particle.facebook import facebook
from particle.twitter import twitter
from particle.promopages import promopages
from particle.rssfeeds import rssfeeds
from particle.facebook import fb
from particle.twitter import twt
from particle.common import DEBUG, db

def init(filepath, obj=None):
  cwd = os.getcwd()
  filepath = os.path.join(cwd, filepath.split("/")[-1])
  # initialize config file
  if obj is None:
    if filepath.endswith('.yml'):
      format ='yaml'
      c = yaml.safe_load(open(filepath))
    elif filepah.endswith('.json'):
      format = 'json'
      c = yaml.safe_load(open(filepath))
  elif isinstance(config, dict):
      format = 'yaml'
      c = obj

  # set environmental variable
  os.environ['PARTICLE_CONFIG_PATH'] = filepath

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
  # for task in tasks:
  #   task.run()
  threaded(tasks, execute, 4, 4)

if __name__ == '__main__':
    import sys
    try:
      config(sys.argv[1])
    except:
      run()


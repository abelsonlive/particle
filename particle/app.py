# -*- coding: utf-8 -*-

from thready import threaded
import json, yaml, os
from optparse import OptionParser
import logging

from particle.facebook import facebook
from particle.twitter import twitter
from particle.promopages import promopages
from particle.rssfeeds import rssfeeds
from particle.facebook import fb
from particle.twitter import twt
from particle.common import DEBUG, db
from particle.helpers import current_datetime

urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.CRITICAL)

class Particle:
  def __init__(self, filepath, config=None):

    # initialize CONFIG
    if config is None:
      if filepath.endswith('.yml'):
        self.CONFIG = yaml.safe_load(open(filepath))
      elif filepah.endswith('.json'):
        self.CONFIG = yaml.safe_load(open(filepath))
    elif isinstance(config, dict):
        self.CONFIG = config

    # generate extended access token     
    self.CONFIG = fb.generate_extended_access_token(self.CONFIG)

    # generate twitter list
    # twt.generate_lists(self.CONFIG)

  def _execute(self, task):
    if task=="twitter":
      twitter.run(self.CONFIG)
    elif task=="facebook":
      facebook.run(self.CONFIG)
    elif task=="rssfeeds":
      rssfeeds.run(self.CONFIG)
    elif task=="promopages":
      promopages.run(self.CONFIG)

  def run(self, 
          tasks=["twitter", "facebook", "rssfeeds", "promopages"], 
          num_threads=2, 
          max_queue=4):
    
    # check if tasks is not a list
    if isinstance(tasks, basestring):
      tasks = [tasks]

    logging.info( "New Job @ %s" % current_datetime(self.CONFIG).strftime('%Y-%m-%d %H:%M:%S') )
    logging.info("\n---------------------------------------\n")

    # run them
    for t in tasks:
      self._execute(t)
    # threaded(tasks, self._execute, num_threads= num_threads,  max_queue = max_queue)

def cl():
  parser = OptionParser()
  parser.add_option("-c", '--config', dest="config", default="particle.yml")
  parser.add_option("-t", '--tasks', dest="tasks", default="twitter,facebook,rssfeeds,promopages")
  (options, args) = parser.parse_args()
  tasks = options.tasks.split(',')
  particle = Particle(filepath=options.config)
  particle.run(tasks = tasks)

if __name__ == '__main__':
  cl()
    
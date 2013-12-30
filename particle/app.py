#!/usr/bin/env python
# -*- coding: utf-8 -*-

from thready import threaded
import yaml, json
import logging

from particle.facebook import facebook
from particle.twitter import twitter
from particle.promopages import promopages
from particle.rssfeeds import rssfeeds
from particle.facebook import fb
from particle.twitter import twt
from particle.common import DEBUG, db
from particle.helpers import *

urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.CRITICAL)

log = logging.getLogger('particle')

class Particle:
  def __init__(self, filepath, config=None):

    # initialize CONFIG
    if config is None:
      if filepath.endswith('.yml'):
        self.CONFIG = yaml.safe_load(open(filepath))
      elif filepah.endswith('.json'):
        self.CONFIG = json.load(open(filepath))
    elif isinstance(config, dict):
      self.CONFIG = config

    # generate extended access token     
    self.CONFIG = fb.generate_extended_access_token(self.CONFIG)

    # generate twitter list
    twt.generate_lists(self.CONFIG)

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
          num_threads=4, 
          max_queue=4):
    
    # check if tasks is not a list
    if isinstance(tasks, basestring):
      tasks = [tasks]

    threaded_or_serial(tasks, self._execute, num_threads, max_queue)

    def __repr__(self):
        return '<Particle>'
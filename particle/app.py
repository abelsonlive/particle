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
  def __init__(self, config, tasks=None):

    self.CONFIG, self.TASKS = load_and_validate_config(config)
    if tasks is not None:
      self.TASKS = tasks

    if 'twitter' in self.TASKS:
      twt.generate_lists(self.CONFIG)
    if 'facebook' in self.TASKS:
      self.CONFIG = fb.generate_extended_access_token(self.CONFIG)

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
          num_threads=4, 
          max_queue=4):
    
    threaded_or_serial(self.TASKS, self._execute, num_threads, max_queue)

    def __repr__(self):
        return '<Particle Object>'
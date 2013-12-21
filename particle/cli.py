#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, yaml, os, sys
from optparse import OptionParser

from particle.web import api
from particle.app import Particle


def cli():
  if sys.argv[1] == 'run':
    parser = OptionParser()
    parser.add_option("-c", '--config', dest="config", default="particle.yml")
    parser.add_option("-t", '--tasks', dest="tasks", default="twitter,facebook,rssfeeds,promopages")
    (options, args) = parser.parse_args()
    tasks = options.tasks.split(',')
    particle = Particle(filepath=options.config)
    particle.run(tasks = tasks)

  elif sys.argv[1] == 'web':
    api()
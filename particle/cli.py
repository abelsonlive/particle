#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, yaml, os, sys
from argparse import ArgumentParser

from particle.web import api
from particle.app import Particle


# sub-command functions
def particle_runner(args):
  tasks = args.tasks.split(',')
  particle = Particle(filepath=args.config)
  particle.run(tasks = tasks)

def api_runner(args):
  api(port = args.port, debug = args.debug)

# command line interface
def cli():
  parser = ArgumentParser(
    prog = 'particle', 
    usage = '%(prog)s [options]', 
    description='Run particle from the command line.'
  )
  subparsers = parser.add_subparsers()
  
  # run particle
  parser_run = subparsers.add_parser('run')
  parser_run.add_argument(
    "-c", '--config', 
    dest="config", 
    default="particle.yml", 
    help="The path to your configuration file.\r\ndefault = particle.yml"
  )
  parser_run.add_argument(
    "-t", '--tasks', 
    dest="tasks", 
    default="twitter,facebook,rssfeeds,promopages", 
    help = 'A comma-separated list of tasks to run.\r\ndefault = twitter,facebook,rssfeeds,promopages'
  )
  parser_run.set_defaults(func=particle_runner)

  parser_api = subparsers.add_parser('api')
  parser_api.add_argument(
    "-p", '--port', 
    dest = "port", 
    default = 3030, 
    help = 'The port on which to serve the API.\r\ndefault = 3030'
  )
  parser_api.add_argument(
    "-d", '--debug', 
    dest = "debug", 
    action='store_true', 
    help = 'Whether or not to run the API in debug mode.\r\ndefault = True'
  )
  parser_api.set_defaults(func=api_runner)

  # parse args and run function
  args = parser.parse_args()
  args.func(args)

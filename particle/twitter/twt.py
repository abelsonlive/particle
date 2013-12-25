#!/usr/bin/python
# -*- coding: utf-8 -*-

import tweepy
from thready import threaded
from particle.common import DEBUG
import logging


def connect(config):
  """
  Given 4 Environmental Variables, Connect to Twitter
  """
  
  # load credentials
  consumer_key = config['twitter']['consumer_key']
  consumer_secret = config['twitter']['consumer_secret']
  access_token = config['twitter']['access_token']
  access_token_secret = config['twitter']['access_token_secret']

  # authenticate
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth)

  return api

def add_list_member(list_member_arg_set):

  screen_name, slug, owner_screen_name, api = list_member_arg_set

  try:
    api.add_list_member(
      owner_screen_name = owner_screen_name,
      slug = slug,
      user_id = screen_name
    )

  except:
    logging.info( "%s doesn't exist" % screen_name )

  else:
    logging.info( "TWT\tadding %s to list: %s for user: %s" % (screen_name, slug, owner_screen_name) )

def generate_list(api, slug, list_dict):

  # parse handles
  if isinstance(list_dict['screen_names'], basestring):
    screen_names = [
      sn.strip() 
      for sn in open(list_dict['screen_names']).read().split("\n") 
      if sn != '' and sn is not None 
    ]

  else:
    screen_names = [sn for sn in list_dict['screen_names'] if sn != '' and sn is not None]
  
  owner_screen_name = list_dict['owner']
  
  try:
    api.create_list(slug)

  except tweepy.error.TweepError as e:
    
    logging.error( "ERROR\tTWT\t%s Already Exists for user %s" % (slug, owner_screen_name) )
    logging.error( e )
    return None

  else:
    # get current list members and member ids:
    members = []
    for member in tweepy.Cursor(api.list_members, owner_screen_name, slug).items():
      
      members.append(member.screen_name)
      members.append(member.id_str)
    
    # add members if they aren't already in list
    list_member_arg_sets = [
      (screen_name, slug, owner_screen_name, api) 
      for screen_name in screen_names if screen_name not in members
    ]
    threaded(list_member_arg_sets, add_list_member, 30, 200)

def generate_lists(config):
  
  logging.info('TWITTER\tupdating lists')

  api = connect(config)
  for slug, list_dict in config['twitter']['lists'].iteritems():
    generate_list(api, slug, list_dict)

def get_list_timelines(config):
  api = connect(config)
  list_list = []
  for slug, list_dict in config['twitter']['lists'].iteritems():
    logging.info( "TWITTER\tgetting new data for twitter.com/%s/lists/%s" % (list_dict['owner'], slug) )
    tweets = api.list_timeline(
            owner_screen_name = list_dict['owner'], 
            slug =  slug,
            count = list_dict['limit']
          )
    list_list.append({slug: [t for t in tweets]})

  return list_list

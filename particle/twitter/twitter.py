#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import tweepy
from thready import threaded
from datetime import datetime
import logging

from particle.twitter import twt
from particle.common import twt_table, DEBUG
from particle.helpers import *

TWT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

log = logging.getLogger('particle')


def parse_tweet(tweet_arg_set):
  
  # parse args
  slug, t, config = tweet_arg_set
    
  # get twt_id
  twt_id = t.id_str

  # check for relevant urls
  raw_urls = [u['expanded_url'] for u in t.entities['urls']]

  # parse urls
  article_urls = set([parse_url(unshorten_link(u, config)) for u in raw_urls])

  if any([is_article(u, config) for u in article_urls]):

    # parse dates
    # sometimes t.created_at is a datetime object
    if isinstance(t.created_at, datetime):
      dt = t.created_at
    else:
      dt = datetime.strptime(t.created_at, TWT_DATE_FORMAT)
    
    date_time = tz_adj(dt, config)
    time_bucket = round_datetime(date_time, config) if date_time is not None else None
    
    raw_timestamp = int(date_time.strftime('%s'))
    
    for article_url in article_urls:
      
      # sluggify url
      article_slug = sluggify(article_url)
      screen_name = t.user.screen_name

    # format data
      data = {
        'article_slug': article_slug,
        'article_url': article_url,
        'time_bucket': time_bucket,
        'raw_timestamp' :  raw_timestamp,
        'twt_list' : slug,
        'twt_post_created': raw_timestamp,
        'twt_id': twt_id,
        'twt_screen_name': t.user.screen_name,
        'twt_text': t.text,
        'twt_followers': t.author.followers_count,
        'twt_friends': t.author.friends_count,
        'twt_lang': t.lang,    
        'twt_raw_links': raw_urls,
        'twt_in_reply_to_screen_name': t.in_reply_to_screen_name,
        'twt_in_reply_to_status_id_str': t.in_reply_to_status_id_str
      }
      
      #
      log.info( "  < twitter > < tweet > < %s > %s" % (t.user.screen_name, article_url) )

      # generate datasource
      data_source = "twitter_%s" % slug
      
      # insert data source
      data['data_source'] = data_source

      # upsert url
      upsert_url(article_url, article_slug, data_source, config)

      # upsert data
      twt_table.upsert(data, ['twt_id'])


def parse_tweets(tweet_arg_sets):
  threaded_or_serial(tweet_arg_sets, parse_tweet, 5, 200)

def run(config):
  try:
    tweet_arg_sets = [
      (slug, t, config) 
      for l in twt.get_list_timelines(config) 
      for slug, tweets in l.iteritems()
      for t in tweets
    ]

  except tweepy.error.TweepError as e:
    log.error(e)

  else:
    parse_tweets(tweet_arg_sets)


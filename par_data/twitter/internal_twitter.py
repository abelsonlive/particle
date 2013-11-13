#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')
import json
import tweepy
from thready import threaded
from datetime import datetime
from par_data.twitter import twt
from par_data.common import db, CONFIG, DEBUG, PRINT_OUTPUT
from par_data.helpers import *

TWT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def parse_tweet(t):

  # check if id exists
  twt_id = t.id_str
  if not db.sismember('internal_twitter_twt_ids', twt_id):

    # if not, add id to id_set
    db.sadd('internal_twitter_twt_ids', twt_id)
    # check for relevant urls
    raw_urls = [u['expanded_url'] for u in t.entities['urls']]
    if any([is_article(u) for u in raw_urls]):

      # parse urls
      article_urls = set([parse_url(unshorten_link(u)) for u in raw_urls])

      # parse dates
      # sometimes t.created_at is a datetime object
      if isinstance(t.created_at, datetime):
        dt = t.created_at
      else:
        dt = datetime.strptrim(t.created_at, TWT_DATE_FORMAT)
      
      date_time = tz_adj(dt)
      time_bucket = round_datetime(date_time) if date_time is not None else None
      
      raw_timestamp = int(date_time.strftime('%s'))
      

      for article_url in article_urls:
        # sluggify url
        article_slug = sluggify(article_url)
        screen_name = t.user.screen_name
        print "INFO: New Tweet - %s/%s - %s" % (screen_name, twt_id, article_slug)

      # format data
        value = {
          'article_slug': article_slug,
          'article_url': article_url,
          'time_bucket': time_bucket,
          'raw_timestamp' :  raw_timestamp,
          'twt_post_created': raw_timestamp,
          'twt_id': twt_id,
          'twt_screen_name': t.user.screen_name,
          'twt_text': t.text,
          'twt_followers': t.author.followers_count,
          'twt_friends': t.author.friends_count,
          'twt_lang': t.lang,    
          'twt_raw_links': raw_urls,
          'twt_hashtags': t.entities['hashtags'],
          'twt_user_mentions': t.entities['user_mentions'],
          'twt_in_reply_to_screen_name': t.in_reply_to_screen_name,
          'twt_in_reply_to_status_id_str': t.in_reply_to_status_id_str
        }
        
        data_source = "twitter_%s" % value['twt_screen_name'] 
        # upsert url
        upsert_url(article_url, data_source)

        value = json.dumps({ data_source : value})
        
        if PRINT_OUTPUT:
          # print debug message to console
          debug_message(article_slug, time_bucket, value)
          
        else:
          # upload data to redis
          db.zadd(article_slug, time_bucket, value)

def parse_tweets(tweets):
    if DEBUG:
      for t in tweets:
        parse_tweet(t)
    else:
      threaded(tweets, parse_tweet, 2, 10)

def run():
    list_owner = CONFIG['twitter']['list_owner']
    list_slug = CONFIG['twitter']['list_slug']
    print "INFO: getting new data for twitter.com/%s/lists/%s" % (list_owner, list_slug)
    try:
        tweets = [t for t in twt.get_list_timeline()]
    except tweepy.error.TweepError as e:
        print e
    else:
        return parse_tweets(tweets)

if __name__ == '__main__':
  run()

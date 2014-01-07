#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from thready import threaded
from pprint import pprint
from datetime import datetime
import logging

from particle.common import db, DEBUG
from particle.facebook import fb
from particle.helpers import *


FB_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S+0000"

log = logging.getLogger('particle')


def is_insights(page_id, config):
  """
  Determine whether we can collect insights for a page
  """
  if config.has_key('insights_pages'):
    return False
  else:
    return page_id in set(config['facebook'])


def get_fb_link(post_data, config, unshorten=False):
  """
  parse fb_post data for links
  """
  if post_data.has_key('link'):
    if unshorten:
      return parse_url(unshorten_link(post_data['link'], config))
    else:
      return parse_url(post_data['link'])
  elif post_data.has_key('source'):
    if unshorten:
      return parse_url(unshorten_link(post_data['source'], config))
    else:
      return parse_url(post_data['source'])
  else:
    return None


def parse_message_urls(message, config):
  """
  parse facebook message for links
  """
  if message is not None:
    message_urls = extract_urls(message, config)
    if len(message_urls)>0:
      return [u for u in message_urls]
    else:
      return []
  else:
    return [] 


def get_message_urls(article_urls, message, config):
  """
  determine whether we should get message_urls
  """
  if len(article_urls)==0:
    return parse_messge_urls(message, config)
  elif article_urls[0] is not None and is_facebook_link(article_urls[0]):
    return parse_message_urls(message, config)
  else:
    return []


def get_insights_data(api, page_id, post_id):
  """
  Get insights data if indicated so by the config file
  """
  graph_results = api.get(post_id + "/insights", page=False, retry=5)
  data = graph_results['data']
  insights = {}
  insights['includes_insights'] = True  
  
  for d in data:
    val = d['values'][0]['value']
    if isinstance(val, dict):
      for k, v in val.iteritems():
        insights[k] = v

    else:
      insights[d['name']] = val

  return insights


def insert_new_post(post_arg_set):
  """
  insert new post into redis
  """
  api, post_data, acct_data, page_id, config = post_arg_set

  try:
    post_id = post_data['id'] if post_data.has_key('id') else None

  except Exception as e:
    log.error( e )

  else:
    if is_insights(page_id, config):
      insights_value = get_insights_data(api, page_id, post_id)
    else:
      insights_value = {}
    
    # parse date
    if post_data.has_key('created_time') and post_data['created_time'] is not None:  
      dt = datetime.strptime(post_data['created_time'], FB_DATE_FORMAT)
      date_time = tz_adj(dt, config)
      time_bucket = round_datetime(date_time, config)
      raw_timestamp = int(date_time.strftime("%s"))
    
    else:
      time_bucket = None
      raw_timestamp = None
    
    # extract message so we can find links within the msg if not in url
    article_urls = [get_fb_link(post_data, config, unshorten=True)]
    message = post_data['message'].encode('utf-8') if post_data.has_key('message') else None
    message_urls = get_message_urls(article_urls, message, config)

    # detect article links, unshorten and parse
    article_urls = [
      parse_url(unshorten_link(url, config)) \
      for url in article_urls + message_urls
      if url is not None
    ]

    article_urls = [url for url in article_urls if is_article(url, config)]

    if article_urls:
      for article_url in set(article_urls):

        # sluggify url
        article_slug = sluggify(article_url)

        # format data
        post_value = {
          'article_slug': article_slug,
          'article_url': article_url,
          'time_bucket': time_bucket,
          'fb_post_created': raw_timestamp,
          'raw_timestamp': raw_timestamp,
          'fb_raw_link' : get_fb_link(post_data, config=config),
          'fb_page_id': page_id,
          'fb_post_id': post_id,
          'fb_page_likes': acct_data['likes'] if acct_data.has_key('likes') else None,
          'fb_page_talking_about': acct_data['talking_about_count'] if acct_data.has_key('talking_about_count') else None,
          'fb_type': post_data['type'] if post_data.has_key('type') else None,
          'fb_status_type': post_data['status_type'] if post_data.has_key('status_type') else None,
          'fb_message': message
        }
          
        # always insert insights data
        if is_insights(page_id, config):
          
          log.info( "INSIGHTS\tAdding data from %s re: %s" % (page_id, article_slug) )
          # 
          data_source = "facebook_insights_%s" % page_id 
          
          # upsert url
          upsert_url(article_url, article_slug, data_source, config)

          # insert id
          db.sadd('facebook_post_ids', post_id)

          # format time bucket
          current_time_bucket = gen_time_bucket(config)
          insights_value['time_bucket'] =  current_time_bucket
          post_value.pop('time_bucket', None)
          
          value = json.dumps({
            data_source : dict(post_value.items() + insights_value.items())
          })

          # upload data to redis
          db.zadd(article_slug, current_time_bucket, value)        
            
        # only insert new posts
        elif not db.sismember('facebook_post_ids', post_id):
          
          log.info( "FACEBOOK\tNew post %s\t%s" % (post_id, article_url) )
          
          # insert id
          db.sadd('facebook_post_ids', post_id)     
          
          # upsert url
          data_source = "facebook_%s" % page_id
          upsert_url(article_url, article_slug, data_source, config)

          value = json.dumps({
            data_source : dict(post_value.items() + insights_value.items())
          })

          # upload data to redis
          db.zadd(article_slug, time_bucket, value)


def get_new_data_for_page(page_arg_set):
  """
  get all new posts on a page
  """
  api, page_id, config = page_arg_set

  log.info( "FACEBOOK\tGetting new data for facebook.com/%s" % page_id )
  
  # fetch account data so we can associate the number of likes with the account AT THAT TIME
  try:
    acct_data = api.get(page_id)
  except Exception as e:
    log.error('FACEBOOK\t%s does not exist' % page_id)
    return None
  else:
    # determine limit
    if is_insights(page_id, config):
      if config['facebook'].has_key('insights_limit'):
        limit = config['facebook']['insights_limit']
      else:
        limit = 200

    else:
      if config['facebook'].has_key('page_limit'):
        limit = config['facebook']['page_limit']
      else:
        limit = 10

    # get last {limit} articles for this page
    page = api.get(page_id + "/posts", page=False, retry=5, limit=limit)
    post_arg_sets = [(api, post_data, acct_data, page_id, config) for post_data in page['data']]
    
    threaded_or_serial(post_arg_sets, insert_new_post, 30, 200)


def run(config):
  """
  get all new posts on all pages
  """
  page_ids = config['facebook']['pages']
  api = fb.connect(config)
  page_arg_sets = [(api, page_id, config) for page_id in set(page_ids)]
  
  threaded_or_serial(page_arg_sets, get_new_data_for_page, 30, 100)


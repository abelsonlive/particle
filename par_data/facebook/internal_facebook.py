#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')

import json
from thready import threaded

from par_data.common import db, CONFIG, DEBUG, PRINT_OUTPUT
from par_data.facebook import fb
from par_data.helpers import *
from pprint import pprint
from datetime import datetime

FB_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S+0000"

def is_insights(page_id):
  """
  Determine whether we can collect insights for a page
  """
  return page_id in set(CONFIG['facebook']['insights_pages'])

# link parsing
def get_fb_link(post_data, unshorten=False):
  """
  parse fb_post data for links
  """
  if post_data.has_key('link'):
    if unshorten:
      return parse_url(unshorten_link(post_data['link']))
    else:
      return parse_url(post_data['link'])
  elif post_data.has_key('source'):
    if unshorten:
      return parse_url(unshorten_link(post_data['source']))
    else:
      return parse_url(post_data['source'])
  else:
    return None

def parse_messge_urls(message):
  """
  parse facebook message for links
  """
  if message is not None:
    message_urls = extract_url(message)
    if len(message_urls)>0:
      return [u for u in message_urls]
    else:
      return []
  else:
    return [] 

def get_message_urls(article_urls, message):
  """
  determine whether we should get message_urls
  """
  if len(article_urls)==0:
    return parse_messge_urls(message)
  elif article_urls[0] is not None and is_facebook_link(article_urls[0]):
    return parse_messge_urls(message)
  else:
    return []

def get_insights_data(api, page_id, post_id):
  """
  Get insights data if indicated so by the config file
  """
  if not is_insights(page_id):
    return {}
  else:  
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
  api, post_data, acct_data, page_id = post_arg_set

  try:
    post_id = post_data['id'] if post_data.has_key('id') else None
  except Exception as e:
    print e
  else:
     # optionally get insights data
    insights_value = get_insights_data(api, page_id, post_id)

    # parse date
    if post_data.has_key('created_time') and post_data['created_time'] is not None:  
      dt = datetime.strptime(post_data['created_time'], FB_DATE_FORMAT)
      date_time = tz_adj(dt)
      time_bucket = round_datetime(date_time)
      raw_timestamp = int(date_time.strftime("%s"))
    
    else:
      time_bucket = None
      raw_timestamp = None
    
    # extract message so we can find links within the msg if not in url
    article_urls = [get_fb_link(post_data, unshorten=True)]
    message = post_data['message'].encode('utf-8') if post_data.has_key('message') else None
    message_urls = get_message_urls(article_urls, message)

    # detect article links, unshorten and parse
    article_urls = [
      parse_url(unshorten_link(article_url)) \
      for article_url in article_urls + message_urls
      if article_url is not None and is_article(article_url)
    ]

    if article_urls:
      for article_url in set(article_urls):

        # sluggify url
        article_slug = sluggify(article_url)

        # format data
        post_value = {
          'article_slug': article_slug,
          'article_url': article_url,
          'time_bucket': time_bucket,
          'fb_post_created': time_bucket,
          'raw_timestamp': raw_timestamp,
          'fb_raw_link' : get_fb_link(post_data),
          'fb_page_id': page_id,
          'fb_post_id': post_id,
          'fb_page_likes': acct_data['likes'] if acct_data.has_key('likes') else None,
          'fb_page_talking_about': acct_data['talking_about_count'] if acct_data.has_key('talking_about_count') else None,
          'fb_type': post_data['type'] if post_data.has_key('type') else None,
          'fb_status_type': post_data['status_type'] if post_data.has_key('status_type') else None,
          'fb_message': message
        }
          
        # always insert insights data
        if is_insights(page_id):
          print "INFO: fetching insights data for - %s - %s" % (page_id, article_slug)
          # 
          data_source = "facebook_insights_%s" % page_id 
          # upsert url
          upsert_url(article_url, data_source)

          # insert id
          db.sadd('facebook_post_ids', post_id)

          # format time bucket
          current_time_bucket = gen_time_bucket()
          insights_value.pop('time_bucket', current_time_bucket)
          post_value.pop('time_bucket', None)
          
          value = json.dumps({
            data_source : dict(post_value.items() + insights_value.items())
          })

          if PRINT_OUTPUT:
            print "INFO: Adding insights data for - %s/%s - %s" % (page_id, post_id, article_slug)
            # print debug message to console
            print_output(article_slug, current_time_bucket, value)

          else:
            # upload data to redis
            db.zadd(article_slug, current_time_bucket, value)        
            
        # only insert new posts
        elif not db.sismember('facebook_post_ids', post_id):
          
          print "INFO: New Post - %s - %s" % (post_id, article_slug)
          
          # insert id
          db.sadd('facebook_post_ids', post_id)     
          
          # upsert url
          data_source = "facebook_%s" % page_id
          upsert_url(article_url, data_source)

          value = json.dumps({
            data_source : dict(post_value.items() + insights_value.items())
          })

          if PRINT_OUTPUT:
            print_output(article_slug, time_bucket, value)
          else:
            # upload data to redis
            db.zadd(article_slug, time_bucket, value)

def get_new_data_for_page(page_arg_set):
  """
  get all new posts on a page
  """
  api, page_id = page_arg_set

  print "INFO: getting new data for facebook.com/%s" % page_id
  
  # fetch account data so we can associate the number of likes with the account AT THAT TIME
  try:
    acct_data = api.get(page_id)
  except Exception as e:
    print e
    return None
  else:
    # determine limit
    if page_id in CONFIG['facebook']['insights_pages']:
      limit = CONFIG['facebook']['insights_limit']
    else:
      limit = CONFIG['facebook']['page_limit']

    # get last 100 articles for this page
    page = api.get(page_id + "/posts", page=False, retry=5, limit=limit)
    if DEBUG:
      for post_data in page['data']:
        post_arg_set = (api, post_data, acct_data, page_id)
        insert_new_post(post_arg_set)
    else:
      post_arg_sets = [(api, post_data, acct_data, page_id) for post_data in page['data']]
      threaded(post_arg_sets, insert_new_post, 20, 150)

def run():
  """
  get all new posts on all pages
  """
  page_ids = CONFIG['facebook']['pages']
  api = fb.connect()
  if DEBUG:
    for page_id in page_ids:
      page_arg_set = (api, page_id)
      get_new_data_for_page(page_arg_set)
  # fetch account data so we can associate the number of likes with the account AT THAT TIME
  else:
    page_arg_sets = [(api, page_id) for page_id in page_ids]
    threaded(page_arg_sets, get_new_data_for_page, 5, 20)

if __name__ == '__main__':
  run()

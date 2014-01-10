#!/usr/bin/env python
# -*- coding: utf-8 -*-

import feedparser
from thready import threaded
from datetime import datetime
from dateutil import parser
import json
import requests
import logging

# custom modules:
from particle.common import rss_table, DEBUG
from particle.rssfeeds.article_extractor import extract_article
from particle.helpers import *

log = logging.getLogger('particle')

def parse_rss_date(entry):
  if entry.has_key('updated_parsed'):
    dt = entry['updated_parsed']
    return datetime(
        dt.tm_year, 
        dt.tm_mon, 
        dt.tm_mday, 
        dt.tm_hour, 
        dt.tm_min, 
        dt.tm_sec
      )
  elif entry.has_key('updated'):
    return parser.parse(entry('updated'))
  else:
    return None

def parse_one_entry(entry_arg_set):
  """
  parse an entry in an rss feed
  """
  entry, data_source, full_text, config = entry_arg_set

  # intitialize data
  data = {}

  # open url to get actual link
  if entry.has_key('link') and entry['link'] != '' and entry['link'] is not None:
  
    # parse url
    article_url =  parse_url(entry['link'])
    article_slug = sluggify(article_url)
    data['article_url'] = article_url
    data['article_slug'] = sluggify(data['article_url'])

    # parse date
    dt = parse_rss_date(entry)
    if dt is not None:
      data['time_bucket'] = round_datetime(dt, config)
      data['raw_timestamp'] = int(dt.strftime('%s'))
      data['pub_date'] = dt.strftime('%Y-%m-%d %H:%M:%S')

    else:
      data['time_bucket'] = gen_time_bucket(config)
      data['raw_timestamp'] = current_timestamp(config)

    # parse_title
    data['rss_title'] = entry.get('title', None)

    # parse content
    if entry.has_key('summary'):
      data['rss_content'] = strip_tags(entry['summary'])
      data['rss_html'] = entry['summary']

  # if feed is not full text, extract the article content
    # by crawling the page
    if not full_text:
      extracted_data = extract_article(article_url)
      # extracted_urls = extract_urls(article_datum['extracted_html'], config, False)
      # extracted_imgs = extract_imgs(article_datum['extracted_html'])
    else:
      extracted_data = {}
      # extracted_urls = extract_urls(rss_html, config, False)
      # extracted_imgs = extract_imgs(rss_html)

      
    # merge data
    rss_data = dict(
      data.items() + 
      extracted_data.items()
    )
    
    # log
    log.info( "  < rssfeeds > < %s > %s" % (data_source, article_url) )

    # upsert the url
    upsert_url(article_url, article_slug, data_source, config)

    # upsert the data
    rss_table.upsert(rss_data, ['article_slug'])

  

def parse_one_feed(feed_arg_set):
  feed_url, data_source, full_text, config = feed_arg_set
  """
  parse all the items in an rss feed
  """
  
  feed_data = feedparser.parse(feed_url)
  
  entries = feed_data['entries']
  entry_arg_sets = [(entry, data_source, full_text, config) for entry in entries]

  threaded_or_serial(entry_arg_sets, parse_one_entry, 30, 100)

def run(config):
  """
  parse all teh feedz
  """
  # generate args from config
  if not isinstance(config['rssfeeds'], dict):
    raise ParticleConfigException("'rssfeeds' field must be a set of key/value pairs.")

  feed_arg_sets = []
  for data_source, v in config['rssfeeds'].iteritems():
    if not v.has_key('full_text'):
      v['full_text'] = False
    feed_arg = (v['feed_url'], data_source, v['full_text'], config)
    feed_arg_sets.append(feed_arg)

  # thread that shit!
  threaded_or_serial(feed_arg_sets, parse_one_feed, 30, 100)

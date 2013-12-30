#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import re
from particle.common import db
from HTMLParser import HTMLParser
from urlparse import urlparse
import pytz
import requests
from pprint import pprint
import string
import json
import logging
from thready import threaded

from particle.common import DEBUG

requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.CRITICAL)

log = logging.getLogger('particle')

# wrapper for thready
def threaded_or_serial(tasks, func, num_threads, max_queue):
  if DEBUG:
    for t in tasks:
      func(t)
  else:
    threaded(tasks, func, num_threads, max_queue)

# debug msg
def print_output(article_url, time_bucket, value):
  log.info( "key: %s" % article_url )
  log.info( "rank: %s" % time_bucket )
  log.info( value )


# DATE HELPERS #
def round_datetime(dt, config):
  """
  round dateime object to set bucket
  return as timestamp integer
  """
  bucket = int(config['global']['bucket'])
  dt = dt - timedelta(
          minutes = dt.minute % bucket,
          seconds = dt.second,
          microseconds = dt.microsecond
      )
  return int(dt.strftime('%s'))

def tz_adj(dt, config):
  tz = config['global']['newsroom_timezone']
  utc = pytz.timezone("UTC")
  mytz = pytz.timezone(tz)
  try:
      dt = dt.replace(tzinfo=utc)
  except:
      return None
  else:
      return mytz.normalize(dt.astimezone(mytz))
# database
def current_datetime(config=None):
  """
  generate datetime bucket for sorted set ranking
  """
  try:
    tz = config['global']['newsroom_timezone']
  except:
    tz = 'UTC'

  mytz = pytz.timezone(tz)
  return datetime.now(tz=mytz)

def current_timestamp(config=None):
  """
  generate datetime bucket for sorted set ranking
  """
  try:
    tz = config['global']['newsroom_timezone']
  except:
    tz = 'UTC'
    
  mytz = pytz.timezone(tz)
  return int(datetime.now(tz=mytz).strftime('%s'))

def gen_time_bucket(config):
  """
  generate datetime bucket for sorted set ranking
  """
  return round_datetime(current_datetime(config), config)

# DATABASE HELPERS

def sluggify(url):
  regex = re.compile('[%s]' % re.escape(string.punctuation))
  o = urlparse(url)
  out = regex.sub(' ', o.path).strip()
  if out.endswith('html'):
    out = out[:-4].strip()
  return re.sub(r"\s+", "-", out).lower()

def upsert_url(article_url, article_slug, data_source, config):
  if not db.sismember('article_set', article_url):
    # add it to the set
    db.sadd('article_set', article_url)

    # insert metadata
    ts = current_timestamp(config)
    value = json.dumps({
      "url" : article_url,
      "slug": article_slug,
      "timestamp" : ts,
      "data_source": data_source
      })
    
    db.zadd('article_sorted_set', ts, value)

def upsert_rss_pub(article_url, article_slug, value):
  if not db.sismember('article_set', article_url):
    # add it to the set
    db.sadd('article_set', article_url)
    
  key = "%s:article" % article_slug
  db.set(key, value)

# urls
def parse_url(url):
  """
  remove url query strings
  """
  o = urlparse(url)
  return  "%s://%s%s" % (o.scheme, o.netloc, o.path)

def is_article(link_url, config):
  patterns = config['global']['content_regexes'] + \
             config['global']['short_regexes']

  if len(patterns)>0:
    return any([re.search(pattern, link_url) for pattern in patterns])
  else:
    return True

# html stripping
class MLStripper(HTMLParser):
  def __init__(self):
    self.reset()
    self.fed = []

  def handle_data(self, d):
    self.fed.append(d)

  def get_data(self):
    return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    raw_text = s.get_data()
    raw_text = re.sub(r'\n|\t', ' ', raw_text)
    return re.sub('\s+', ' ', raw_text).strip()

def is_short_link(url):
  re_short_links = [
    re.compile(r".*bit\.do.*"),
    re.compile(r".*t\.co.*"),
    re.compile(r".*go2\.do.*"),
    re.compile(r".*adf\.ly.*"),
    re.compile(r".*goo\.gl.*"),
    re.compile(r".*bitly\.com.*"),
    re.compile(r".*bit\.ly.*"),
    re.compile(r".*tinyurl\.com.*"),
    re.compile(r".*ow\.ly.*"),
    re.compile(r".*bit\.ly.*"),
    re.compile(r".*adcrun\.ch.*"),
    re.compile(r".*zpag\.es.*"),
    re.compile(r".*ity\.im.*"),
    re.compile(r".*q\.gs.*"),
    re.compile(r".*lnk\.co.*"),
    re.compile(r".*viralurl\.com.*"),
    re.compile(r".*is\.gd.*"),
    re.compile(r".*vur\.me.*"),
    re.compile(r".*bc\.vc.*"),
    re.compile(r".*yu2\.it.*"),
    re.compile(r".*twitthis\.com.*"),
    re.compile(r".*u\.to.*"),
    re.compile(r".*j\.mp.*"),
    re.compile(r".*bee4\.biz.*"),
    re.compile(r".*adflav\.com.*"),
    re.compile(r".*buzurl\.com.*"),
    re.compile(r".*xlinkz\.info.*"),
    re.compile(r".*cutt\.us.*"),
    re.compile(r".*u\.bb.*"),
    re.compile(r".*yourls\.org.*"),
    re.compile(r".*fun\.ly.*"),
    re.compile(r".*hit\.my.*"),
    re.compile(r".*nov\.io.*"),
    re.compile(r".*crisco\.com.*"),
    re.compile(r".*x\.co.*"),
    re.compile(r".*shortquik\.com.*"),
    re.compile(r".*prettylinkpro\.com.*"),
    re.compile(r".*viralurl\.biz.*"),
    re.compile(r".*longurl\.org.*"),
    re.compile(r".*tota2\.com.*"),
    re.compile(r".*adcraft\.co.*"),
    re.compile(r".*virl\.ws.*"),
    re.compile(r".*scrnch\.me.*"),
    re.compile(r".*filoops\.info.*"),
    re.compile(r".*linkto\.im.*"),
    re.compile(r".*vurl\.bz.*"),
    re.compile(r".*fzy\.co.*"),
    re.compile(r".*vzturl\.com.*"),
    re.compile(r".*picz\.us.*"),
    re.compile(r".*lemde\.fr.*"),
    re.compile(r".*golinks\.co.*"),
    re.compile(r".*xtu\.me.*"),
    re.compile(r".*qr\.net.*"),
    re.compile(r".*1url\.com.*"),
    re.compile(r".*tweez\.me.*"),
    re.compile(r".*sk\.gy.*"),
    re.compile(r".*gog\.li.*"),
    re.compile(r".*cektkp\.com.*"),
    re.compile(r".*v\.gd.*"),
    re.compile(r".*p6l\.org.*"),
    re.compile(r".*id\.tl.*"),
    re.compile(r".*dft\.ba.*"),
    re.compile(r".*aka\.gr.*")
  ]
  return any([r.search(url) for r in re_short_links])


def is_facebook_link(link):
  if re.search("facebook", link):
    return True
  else:
    return False

def test_for_short_link(link, config):
  patterns = config['global']['short_regexes']
  if any([re.search(p, link) for p in patterns]):
    return True
  elif is_short_link(link):
    return True
  else:
    return False

def unshorten_link(link, config):
  """
  recursively unshorten a link
  """
  l = link
  test = test_for_short_link(l, config)
  if test:
    tries = 0
    while test:
      
      try:
        r = requests.get(l)
      
      except Exception as e:
        log.warning("unshorten_link, %s" % e)
        
        # quit
        return l
        break

      else:
        
        # quit
        if r.status_code != 200:
          return l
          break
        
        # give it one more shot!
        else:
          l = r.url
          test = test_for_short_link(l, config)
          tries +=1
          
          # if we've tried 10 times, give up
          if tries==10:
            return l
            break

    # return link at final state
    return l
  else:
    return link

def extract_url(s, config):
    """
    get urls from input string
    """
    pattern = "(https?://[^\s]+)"
    return [unshorten_link(l, config) for l in re.findall(pattern, s) if len(l)>5]


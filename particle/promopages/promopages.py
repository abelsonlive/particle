#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from datetime import datetime, timedelta
from thready import threaded
import json, yaml
import socket

from particle.common import pp_table, DEBUG
from particle.helpers import *

log = logging.getLogger('particle')

# set the socket timeout
socket.setdefaulttimeout(20)

def get_image_for_a_link(link):
  try:
    img = link.find_element_by_tag_name("img")
  except NoSuchElementException:
    img = None
  if img is not None:
    w = int(img.get_attribute("width"))
    h = int(img.get_attribute("height"))
    
    return dict(
      pp_is_img = 1,
      pp_img_width = w,
      pp_img_height = h,
      pp_img_area = w*h,
      pp_img_src = img.get_attribute("src")
    )
  else:
    return dict(pp_is_img = 0)


def scrape_link(link_arg_set):
  promo_url, link, time_bucket, data_source, config = link_arg_set

  try:
    link_url = link.get_attribute("href")

  except StaleElementReferenceException:
    pass

  else:                  
    # continue under specified conditions
    if isinstance(link_url, basestring) and is_article(link_url, config):
      
      # parse link text
      try:
        link_text = link.text.encode('utf-8').strip()
      except:
        link_text = None

      if link_text is not None  and link_text is not '':

        pos_x = int(link.location['x'])
        pos_y = int(link.location['y'])

        if pos_x > 0 and pos_y > 0:
          # okay, let's record it

          # get image
          img_dict = get_image_for_a_link(link)

          # parse link
          link_url = link_url.encode('utf-8')
          article_url = parse_url(link_url)

          # sluggify
          article_slug = sluggify(article_url)

          # scrape
          log.info("  < promopage > < %s > %s" % (data_source, article_url))

          link_dict = {
            'article_slug' : article_slug,
            'article_url': article_url,
            'time_bucket': time_bucket,
            'raw_timestamp': int(datetime.now().strftime("%s")),
            'pp_promo_url' : promo_url,
            'pp_link_url': link_url,
            'pp_headline' : link_text,
            'pp_font_size' : int(link.value_of_css_property('font-size')[:-2]),
            'pp_pos_x' : pos_x,
            'pp_pos_y' : pos_y
          }

          data = dict(img_dict.items() + link_dict.items())          

          # insert data
          pp_table.insert(data)


def scrape_links(links_arg_set):    
  
  b, promo_url, data_source, config = links_arg_set
  log.info( "  < promopages > < %s > fetching" % data_source )
  time_bucket = gen_time_bucket(config)
  links = b.find_elements_by_tag_name("a")
  link_arg_sets = [(promo_url, l, time_bucket, data_source, config) for l in links]
  
  threaded_or_serial(link_arg_sets, scrape_link, 5, 25)
  # for link_arg_set in link_arg_sets:
  #   scrape_link(link_arg_set)

def readystate_complete(d):
    # AFAICT Selenium offers no better way to wait for the document to be loaded,
    # if one is in ignorance of its contents.
    return d.execute_script("return document.readyState") == "complete"


def get_url_safely(b, url):
  tries = 0
  try:
    b.get(url)
    WebDriverWait(b, 30).until(readystate_complete)
  
  except TimeoutException:
    d.execute_script("window.stop();")

  except socket.timeout:
    while 1:

      try:
        b.get(url)
        WebDriverWait(b, 5).until(readystate_complete)
  
      except TimeoutException:
        d.execute_script("window.stop();")

      except:
        tries += 1
        if tries == 20:
          return b
      else:
        return b

  except Exception as e:
    return b

  else:
    return b


def scrape_promo_page(page_arg_set):
  promo_url, data_source, config = page_arg_set
  b = webdriver.PhantomJS(config['global']['phantomjs'])
  b = get_url_safely(b, promo_url)
  links_arg_set = (b, promo_url, data_source, config)
  scrape_links(links_arg_set)


def run(config):
  pages = config['promopages']
  page_arg_sets = [(url, slug, config) for slug, url in pages.iteritems()] 
  threaded_or_serial(page_arg_sets, scrape_promo_page, 5, 100)


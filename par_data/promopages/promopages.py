#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from par_data.common import db, CONFIG, DEBUG, PRINT_OUTPUT
from par_data.helpers import *
from datetime import datetime, timedelta
from thready import threaded
import json

def get_image_for_a_link(link):
    try:
        img = link.find_element_by_tag_name("img")
    except NoSuchElementException:
        img = None
    if img is not None:
        return dict(
                is_img = 1,
                img_width = img.get_attribute("width"),
                img_height = img.get_attribute("height"),
                img_src = img.get_attribute("src")
                )
    else:
        return dict(is_img=0)

def scrape_link(arg_set):
    promo_url, link, time_bucket, data_source = arg_set
    try:
        link_url = link.get_attribute("href")
    except StaleElementReferenceException:
        pass
    else:
        test = link_url is not None and isinstance(link_url, basestring) and is_article(link_url)
        if test:
            # parse link
            link_url = link_url.encode('utf-8')
            article_url = parse_url(unshorten_link(link_url))
        
            # sluggify
            article_slug = sluggify(article_url)

            # scrape
            print "INFO: grabbing promo data for - " + article_slug + " - " + promo_url

            img_dict = get_image_for_a_link(link)

            link_dict = {
                'article_slug' : article_slug,
                'article_url': article_url,
                'time_bucket': time_bucket,
                'raw_timestamp': int(datetime.now().strftime("%s")),
                'pp_promo_url' : promo_url,
                'pp_link_url': link_url,
                'pp_headline' : link.text.encode('utf-8').strip(),
                'pp_font_size' : link.value_of_css_property('font-size'),
                'pp_pos_x' : link.location['x'],
                'pp_pos_y' : link.location['y']
            }
            # upsert url
            upsert_url(article_url, data_source)
            
            value = json.dumps({data_source : dict(img_dict.items() + link_dict.items())})

            if PRINT_OUTPUT:
              # print debug message to console
              print_output(article_slug, time_bucket, value)
              
            else:
              # upload data to redis
              db.zadd(article_slug, time_bucket, value)

def scrape_links(links_arg_set):
    b, promo_url, data_source = links_arg_set
    print "INFO: HITTING %s" % promo_url
    time_bucket = gen_time_bucket()
    links = b.find_elements_by_tag_name("a")
    link_arg_sets = [(promo_url, l, time_bucket, data_source) for l in links]
    for link_arg_set in link_arg_sets:
        scrape_link(link_arg_set)

def scrape_promo_page(page_arg_set):
    promo_url, data_source = page_arg_set
    b = webdriver.PhantomJS()
    b.get(promo_url)
    arg_set = (b, promo_url, data_source)
    scrape_links(arg_set)

def run():
  pages = CONFIG['promopages']
  if DEBUG:
    for slug, url in pages.iteritems():
      page_arg_set = (url, slug)
      scrape_promo_page(page_arg_set)
  else:
    page_arg_sets = [(url, slug) for slug, url in pages.iteritems()]
    threaded(page_arg_sets, scrape_promo_page, 2, 2)
      

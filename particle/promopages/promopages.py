#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from particle.common import db, CONFIG, DEBUG
from particle.helpers import *
from datetime import datetime, timedelta
from thready import threaded
import json

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
        return dict(pp_is_img=0)

def scrape_link(link_arg_set):
    promo_url, link, time_bucket, data_source = link_arg_set

    try:
        link_url = link.get_attribute("href")
    except StaleElementReferenceException:
        pass
    else:
        # parse link text
        try:
            link_text = link.text.encode('utf-8').strip()
        except:
            link_text = None
        
        # det image
        img_dict = get_image_for_a_link(link)

        # tests 
        test_link = link_url is not None and isinstance(link_url, basestring) and is_article(link_url)
        test_text = link_text is not None  and link_text is not ''
        test_image = True if img_dict['pp_is_img']==1 else False
        test_existence = True if link.location['x'] > 0 or link.location['y'] > 0 else False

        # continue under certain conditions
        if all([any([test_image, test_text]), test_link, test_existence]):

            # parse link
            link_url = link_url.encode('utf-8')
            article_url = parse_url(unshorten_link(link_url))

            # sluggify
            article_slug = sluggify(article_url)

            # scrape
            print "INFO\tPROMOPAGE\tlink detected on %s re: %s" % (promo_url, article_slug)

            link_dict = {
                'article_slug' : article_slug,
                'article_url': article_url,
                'time_bucket': time_bucket,
                'raw_timestamp': int(datetime.now().strftime("%s")),
                'pp_promo_url' : promo_url,
                'pp_link_url': link_url,
                'pp_headline' : link_text,
                'pp_font_size' : link.value_of_css_property('font-size'),
                'pp_pos_x' : link.location['x'],
                'pp_pos_y' : link.location['y']
            }

            value = json.dumps({data_source : dict(img_dict.items() + link_dict.items())})

            # upsert url
            upsert_url(article_url, article_slug, data_source)
            # upload data to redis
            db.zadd(article_slug, time_bucket, value)


def scrape_links(links_arg_set):
    b, promo_url, data_source = links_arg_set
    print "INFO\tPROMOPAGE\t%s" % promo_url
    time_bucket = gen_time_bucket()
    links = b.find_elements_by_tag_name("a")
    link_arg_sets = [(promo_url, l, time_bucket, data_source) for l in links]
    for link_arg_set in link_arg_sets:
        try:
            scrape_link(link_arg_set)
        except StaleElementReferenceException as e:
            print "WARNING\t", e
            continue


def scrape_promo_page(page_arg_set):
    promo_url, data_source = page_arg_set
    b = webdriver.PhantomJS()
    b.get(promo_url)
    links_arg_set = (b, promo_url, data_source)
    scrape_links(links_arg_set)

def run():
  pages = CONFIG['promopages']
  if DEBUG:
    for slug, url in pages.iteritems():
      page_arg_set = (url, slug)
      scrape_promo_page(page_arg_set)
  else:
    page_arg_sets = [(url, slug) for slug, url in pages.iteritems()]
    threaded(page_arg_sets, scrape_promo_page, 2, 10)
      

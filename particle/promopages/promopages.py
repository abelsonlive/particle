#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from datetime import datetime, timedelta
from thready import threaded
import json, yaml

from particle.common import db, DEBUG
from particle.helpers import *

# @profile
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

# @profile
def scrape_link(link_arg_set):
    try:
        promo_url, link, time_bucket, data_source, config = link_arg_set

        try:
            link_url = link.get_attribute("href")
        except StaleElementReferenceException:
            pass
        else:            
            
            # continue under specified conditions
            if link_url is not None and isinstance(link_url, basestring) and is_article(link_url, config):
                
                # parse link text
                try:
                    link_text = link.text.encode('utf-8').strip()
                except:
                    link_text = None

                if link_text is not None  and link_text is not '':

                    if link.location['x'] > 0 and link.location['y'] > 0:
                        
                        # get image
                        img_dict = get_image_for_a_link(link)

                        # parse link
                        link_url = link_url.encode('utf-8')
                        article_url = parse_url(link_url)

                        # sluggify
                        article_slug = sluggify(article_url)

                        # scrape
                        logging.info( "PROMOPAGE\tlink detected on %s re: %s" % (promo_url, article_slug) )

                        link_dict = {
                            'article_slug' : article_slug,
                            'article_url': article_url,
                            'time_bucket': time_bucket,
                            'raw_timestamp': int(datetime.now().strftime("%s")),
                            'pp_promo_url' : promo_url,
                            'pp_link_url': link_url,
                            'pp_headline' : link_text,
                            'pp_font_size' : int(link.value_of_css_property('font-size')[:-2]),
                            'pp_pos_x' : int(link.location['x']),
                            'pp_pos_y' : int(link.location['y'])
                        }

                        value = json.dumps({data_source : dict(img_dict.items() + link_dict.items())})

                        # upsert url
                        upsert_url(article_url, article_slug, data_source, config)

                        # upload data to redis
                        db.zadd(article_slug, time_bucket, value)

    except StaleElementReferenceException as e:
        logging.warning( e )

# @profile
def scrape_links(links_arg_set):
    
    b, promo_url, data_source, config = links_arg_set
    
    logging.info( "PROMOPAGE\t%s" % promo_url )
    
    time_bucket = gen_time_bucket(config)
    
    links = b.find_elements_by_tag_name("a")
    
    link_arg_sets = [(promo_url, l, time_bucket, data_source, config) for l in links]
    
    # for link_arg_set in link_arg_sets:
    #     scrape_link(link_arg_set)

    threaded(link_arg_sets, scrape_link, 5, 20)

def scrape_promo_page(page_arg_set):
    promo_url, data_source, config = page_arg_set
    b = webdriver.PhantomJS(config['global']['phantomjs'])
    b.get(promo_url)
    links_arg_set = (b, promo_url, data_source, config)
    scrape_links(links_arg_set)

def run(config):
  pages = config['promopages']
  if DEBUG:
    for slug, url in pages.iteritems():
      page_arg_set = (url, slug, config)
      scrape_promo_page(page_arg_set)
  else:
    page_arg_sets = [(url, slug, config) for slug, url in pages.iteritems()]
    threaded(page_arg_sets, scrape_promo_page, 5, 20)

if __name__ == '__main__':

    config = yaml.safe_load(open('../../particle.yml'))
    run(config)

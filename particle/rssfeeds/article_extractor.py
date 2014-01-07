#!/usr/bin/env python
# -*- coding: utf-8 -*-

from boilerpipe.extract import Extractor
from readability.readability import Document
import requests

from particle.helpers import *
import logging


def extract_article(url, config):
  
  r = requests.get(url)
  
  # the the url exists, continue
  if r.status_code == 200:
    
    # extract and parse response url
    url = parse_url(r.url)

    # extract html
    html = r.content.decode('utf-8', errors='ignore')

    # run boilerpipe
    BP = Extractor(html=html)

    # run readability
    Rdb = Document(html)

    # return article data
    return {
      'extracted_title': Rdb.short_title().strip(),
      'extracted_content': strip_tags(BP.getText()),
      'extracted_html': Rdb.summary()
    }

  # otherwise return an empty dict
  else:
    return {}

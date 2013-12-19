#!/usr/bin/python
# (CC-by) 2010 Copyleft Michal Karzynski, GenomikaStudio.com 
import datetime
import gdata.analytics.client
import gdata.sample_util
import yaml
from datetime import datetime
from particle.helpers import *
import logging

GOOGlE_DATE_FORMAT = "%Y%m%d%H"

def parse_gdata_date(ds):
    return datetime.strptime(ds, GOOGlE_DATE_FORMAT)

def connect(config):
    source_app_name = config['google_analytics']['source_app_name']
    email = config['google_analytics']['email']
    password = config['google_analytics']['password']

    api = gdata.analytics.client.AnalyticsClient(source=source_app_name)
    api.client_login(
        email,
        password,
        source = source_app_name,
        service = api.auth_service,
        account_type = 'GOOGLE',
    )
    return api
 
def query(api, query):
    project_ids = config['google_analytics']['project_ids']
    data_query = gdata.analytics.client.DataFeedQuery(})
 
    feed = api.GetDataFeed(data_query)
    return feed

def parse_query_results(feed):
    data = []
    for e in feed.entry:
        row = {}
        for d in e.dimension:
            var = d.name[3:].lower()
            if var == 'pagepath':
                row['article_slug'] = sluggify(d.value)
            elif var == 'datehour':
                dt = parse_gdata_date(d.value)
                row['timestamp'] = int(dt.strftime("%s"))
            else:
                row[var] = d.value
        for m in e.metric:
            row[m.name[3:].lower()] = m.value
        data.append(row)
    return data

if __name__ == '__main__':
    config = yaml.safe_load(open('../../particle.yml'))
    api = connect(config)
    feed = query(api, config)
    results = parse_query_results(feed)
    print results



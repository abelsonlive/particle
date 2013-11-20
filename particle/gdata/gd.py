#!/usr/bin/python
# (CC-by) 2010 Copyleft Michal Karzynski, GenomikaStudio.com 
import datetime
import gdata.analytics.client
import gdata.sample_util
import yaml

config = yaml.safe_load(open('../../particle.yml'))
source_app_name = config['google_analytics']['source_app_name']
email = config['google_analytics']['email']
password = config['google_analytics']['password']
project_ids = config['google_analytics']['project_ids']

my_client = gdata.analytics.client.AnalyticsClient(source=source_app_name)
my_client.client_login(
    email,
    password,
    source=source_app_name,
    service=my_client.auth_service,
    account_type = 'GOOGLE',
)
 
account_query = gdata.analytics.client.AccountFeedQuery()
data_query = gdata.analytics.client.DataFeedQuery({
    'ids': 'ga:%s' % str(project_ids[0]),
    'dimensions': '', #ga:source,ga:medium
    'metrics': 'ga:pageviews',
    'start-date': '2011-08-06',
    'end-date': '2013-11-18',
    'prettyprint': 'true',
    })
 
feed = my_client.GetDataFeed(data_query)
result = [{x.name: x.value} for x in feed.entry[0].metric]
print result

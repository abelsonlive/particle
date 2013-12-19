import bitly_api

def connect(config):
  api = bitly_api.Connection(config['bitly']['access_token'])
  return api

def lookup_global_hash(api, url):
  res = api.shorten(url)
  return res['global_hash']

    
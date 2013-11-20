import pytumblr

def connect_to_tumblr(conf='haikugrams_tumblr.yml'):
    c = yaml.safe_load(open(conf).read())
    return pytumblr.TumblrRestClient(c['consumer_key'], c['consumer_secret'], c['oauth_token'], c['oauth_token_secret'])

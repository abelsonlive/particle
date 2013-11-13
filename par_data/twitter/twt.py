#!/usr/bin/python
# -*- coding: utf-8 -*-
# import sys
# sys.path.append('../../')

import tweepy
from par_data.common import CONFIG, DEBUG

def connect():
	"""
	Given 4 Environmental Variables, Connect to Twitter
	"""
	
	# load credentials
	consumer_key = CONFIG['twitter']['consumer_key']
	consumer_secret = CONFIG['twitter']['consumer_secret']
	access_token = CONFIG['twitter']['access_token']
	access_token_secret = CONFIG['twitter']['access_token_secret']

	# authenticate
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	return api

def generate_list():
	# parse handles
	if isinstance(CONFIG['twitter']['list_screen_names'], basestring):
		screen_names = [CONFIG['twitter']['list_screen_names']]
	else:
		screen_names = CONFIG['twitter']['list_screen_names']

	api = connect()
	try:
		slug = CONFIG['twitter']['list_slug']
		owner_screen_name = CONFIG['twitter']['list_owner']
		api.create_list(slug)

	except tweepy.error.TweepError as e:
		print "ERROR\tTWT\t%s Already Exists for user %s" % (slug, owner_screen_name)
		print e
		return None
	else:
		for screen_name in screen_names:
			try:
				api.add_list_member(
					owner_screen_name = owner_screen_name,
					slug = slug,
					screen_name = screen_name
				)
			except:
				print "%s doesn't exist" % screen_name
			else:
				print "INFO\tTWT\tadding %s to list: %s for user: %s" % (screen_name, slug, owner_screen_name)

def get_list_timeline():
	api = connect()
	list_tweets = api.list_timeline(
					owner_screen_name = CONFIG['twitter']['list_owner'], 
					slug =  CONFIG['twitter']['list_slug'],
					count = CONFIG['twitter']['limit']
				)
	return [lt for lt in list_tweets]

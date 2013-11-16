#!/usr/bin/python
# -*- coding: utf-8 -*-

import tweepy
from particle.common import DEBUG

def connect(config):
	"""
	Given 4 Environmental Variables, Connect to Twitter
	"""
	
	# load credentials
	consumer_key = config['twitter']['consumer_key']
	consumer_secret = config['twitter']['consumer_secret']
	access_token = config['twitter']['access_token']
	access_token_secret = config['twitter']['access_token_secret']

	# authenticate
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	return api

def generate_list(config):

	# parse handles
	if isinstance(config['twitter']['list_screen_names'], basestring):
		screen_names = [config['twitter']['list_screen_names']]
	else:
		screen_names = config['twitter']['list_screen_names']
	
	slug = config['twitter']['list_slug']
	owner_screen_name = config['twitter']['list_owner']
	
	api = connect(config)
	try:
		api.create_list(slug)

	except tweepy.error.TweepError as e:
		print "ERROR\tTWT\t%s Already Exists for user %s" % (slug, owner_screen_name)
		print e
		return None
	else:
		# get current screen names
		list_members = frozenset([m.screen_name for m in  api.list_members(owner_screen_name, slug)])
		for screen_name in screen_names:
			if screen_name not in list_members:
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

def get_list_timeline(config):
	api = connect(config)
	list_tweets = api.list_timeline(
					owner_screen_name = config['twitter']['list_owner'], 
					slug =  config['twitter']['list_slug'],
					count = config['twitter']['limit']
				)
	return [lt for lt in list_tweets]

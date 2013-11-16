particle
========
`particle` is a tool for collecting data about links on Twitter, Facebook, Webpages, and RSS feeds (for now). It joins this data together by a common url and bucketed timestamp.  This enables analysis similar to that which I discuss in this [blog post](http://brianabelson.com/open-news/2013/11/14/Pageviews-above-replacement.html). `particle` is like [`pollster`](https://github.com/stdbrouw/pollster) but not as developed and nowhere near as sophisticated. I just didn't want to bother learning coffeescript so I built my own version :).

## Configuration
----------------

`particle` runs off of a yaml config file which contains information about the data sources you want to collect, referred to here as `particle.yml`. If you want to see an example of such a file, check out [this one](http://github.com/abelsonlive/particle/examples/nytimes/nytimes.yml), though we'll discuss it in more detail below.

When you start a new `particle` project, you'll want to tell `particle` where this file is:
```
import particle.run as particle

particle.init('~/particle.yml')
```
This one function will read in your configuration file, set it as an environmental variable (`PARTICLE_CONFIG_PATH`), build a Twitter list of the the handles you want to follow, and insert a stable facebook API key (more on all this below).

Now you're all set to run `particle`:
```
particle.run()
```

## `particle.yml`
-----------------

### Global settings

#### URLs
`particle` tries really hard to find specific links around the web. You can set the patterns of these links in `particle.yml`:

```
global:
  content_regexes:
  - .*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*
  short_regexes:
  - nyti\.ms/\w+

```

`content_regexes` represents a list of regular expressions you want to use to detect links to content. In this case, I've written a regular expression that will find links to New York Times content.

```
  content_regexes:
  - .*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*
  - .*propublica.org/[a-z]+/[a-z0-9/-]+
```

This list can be as long or as short as you'd like. For instance:

```
  content_regexes:
  - .*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*
  - .*propublica.org/[a-z]+/[a-z0-9/-]+
```

`short_regexes` represents a list of regular expressions you want to use to detect shortened links to content - they usually show up on Facebook and Twitter.  `particle` will then unshorten these links so that you can resolve them with regular links.

#### Time
`particle` unionizes these URLs in time, so you don't have to join all the data together yourself. It does this by taking in an arbitrary `bucket` parameter representing the number of minutes you'd like to round timestamps down to. This value should correspond to how often you run `particle`. Don't worry though, `particle` will still retain the raw timestamp in case you want more granular events. In addition, `particle` will also resolve all UTC timestamps to the local time zone where your content is published or promoted. In `particle.yml` this looks like:
```
global:
  bucket: 10
  newsroom_timezone: America/New_York
```

Putting it all together, your `global` settings should look something like this:

```
global:
  bucket: 10
  content_regexes:
  - .*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*
  newsroom_timezone: America/New_York
  short_regexes:
  - nyti\.ms/\w+
```

### Data Sources
`particle` currently supports collection from four data sources:
  - Twitter
  - Facebook
  - RSS Feeds
  - Web Pages (we'll call them 'Promo Pages below')

Let's go through each of these and discuss how to customize your `particle` project to your needs.

#### Twitter

###### API

`particle` follows an arbitrary list of Twitter accounts and detects when relevant links are shared. To set this up, you'll first have to [register an app with Twitter](http://dev.twitter.com) and obtain a set of API keys. Once you have these keys, you can enter them into `particle.yml` like so:
```
twitter:
  access_token: xxx
  access_token_secret: xxx
  consumer_key: xxx
  consumer_secret: xxx

```
###### Data
In order to better enable following many hundreds of Twitter acounts, `particle` builds a custom Twitter list and then listens for updates. You can build this list by providing three parameters: the screen name associated with your API keys, the name of the list you want to build, and a list of the screen names you want to follow. This list is built when you run `particle.init()`. In `particle.yml` this looks like this:

```
  lists:
    pardata-test:
      list_owner: brianabelson
      list_screen_names:
        - nytimes
        - nytimesworld
```

You can also set the maximum number of of posts to search through at any given time. Currently the maximum is 200. However, so long as you regularly poll Twitter, you can be relatively certain that you won't miss any tweets. You can set this value in `particle.yml` like so:

```
  limit: 200
```

Putting it all together, your `twitter` settings should look something like this:

```
twitter:
  access_token: xxx
  access_token_secret: xxx
  consumer_key: xxx
  consumer_secret: xxx
  list_owner: brianabelson
  list_slug: pardata-test
  list_screen_names:
  - nytimes
  - nytimesworld
```

#### Facebook

###### API

As with Twitter, you'll need to register an app with Facebook to access their data. You can do that on [here](https://developers.facebook.com/apps).

```
facebook:
  app_id: xxx
  app_secret: xxx
  temp_access_token: xxx
```

One annoyting thing about the Facebook API is that it requires you to hit a particular endpoint to register a stable access token, or an API key that lasts more than a couple of hours. `particle` helps solve this by generating a stable access token for you. However, you'll first need a temporary access token - `temp_access_token` above. You can obtain one of these by going to [https://developers.facebook.com/tools](https://developers.facebook.com/tools) and make sure you are using it with the App you've registered above. You can then press "Get Access Token" and copy that string into `particle.yml`. When you run `particle.init()`, a stable access token will be generated using your temporary access token and insterted into `particle.yml`:

```
facebook:
  app_id: xxx
  app_secret: xxx
  temp_access_token: xxx
  stable_access_token: xxx
  stable_access_token_expires_at: 0123456789
```

Here, `stable_access_token_expires_at` connotes the time at which this so-called "stable" access token will expire - usually about three months.  However, if you simply remove `stable_access_token` from `particle.yml`. regenerate a temporary access token, and re-run `particle.init()`, `particle` will create a new stable access token for you.

###### Data
`particle` collects information about posts on particular facebook pages. Like Twitter, it does this by following a list of page slugs.

```
  pages:
  - nytimes
```

Once again, you can specify the number of posts to look through for each user name, now called `page_limit`(you'll see why, below).

```
  page_limit: 10
```

In addition, if you have access to the [Insights](https://www.facebook.com/help/search/?q=insights) accounts for a set of pages, `particle` can grab highly detailed information about how people engaged with posts on these pages over time. You can specify this in `particle.yml` as follows:

```
  insights_pages:
  - nytimes
```

In this case, you'll want to set the limit (x) according to the number of posts you'd like to track at any one time.  In this logic, when a post first goes live, it will be tracked until x more posts have been published.  Usually I just leave this at it's maximum: 200:

```
  insights_limit: 200
```

Putting it all together, your `twitter` settings should look something like this:

```
facebook:
  app_id: xxx
  app_secret: xxx
  temp_access_token: xxx
  stable_access_token: xxx
  stable_access_token_expires_at: 0123456789
   pages:
  - nytimes
  insights_pages:
  - nytimes 
  insights_limit: 200
```

particle
========
`particle` is a tool for collecting data about links on Twitter, Facebook, Webpages, and RSS feeds (for now). It joins this data together by a common url and bucketed timestamp.  This enables analysis similar to that which I discuss in this [blog post](http://brianabelson.com/open-news/2013/11/14/Pageviews-above-replacement.html). `particle` is like [`pollster`](https://github.com/stdbrouw/pollster) but not as developed and nowhere near as sophisticated. I just didn't want to bother learning coffeescript so I built my own version :).

## Configuration
----------------

`particle` runs off of a yaml config file which contains information about the data sources you want to collect, referred to here as `particle.yml`. If you want to see an example of such a file, check out [this one](http://github.com/abelsonlive/particle/examples/nytimes/nytimes.yml), though we'll discuss it in more detail below.

When you start a new `particle` project, you'll want to tell `particle` where this file is:
```
import particle.run as particle

particle.config('~/particle.yml')
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
`content_regexes` represents a list of regular expressions you want to use to detect links to content. In this case, I've written a regular expression that will find links to New York Times content.  This list can be as long or as short as you'd like. For instance:
```
  content_regexes:
  - .*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*
  - .*propublica.org/[a-z]+/[a-z0-9/-]+
```

`short_regexes` represents a list of regular expressions you want to use to detect shortened links to content - they usually show up on Facebook and Twitter.  `particle` will then unshorten these links so that you can resolve them with regular links.

#### Time
`particle` then unionizes these URLs in time, so you don't have to join all the data together yourself. It does this by taking in an arbitrary `bucket` parameter representing the number of minutes you'd like to round timestamps down to. Don't worry though, `particle` will still retain the raw timestamp in case you want more granular events. In addition, `particle` will also resolve all UTC timestamps to the local time zone where your content is published or promoted. In the `particle.yml` this looks like:
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
`particle` follows an arbitrary list of Twitter accounts and detects when relevant links are shared. To set this up, you'll first have to [register an app with Twitter](http://dev.twitter.com) and obtain a set of API keys. Once you have these keys, you can enter them into `particle.yml` like so:
```
twitter:
  access_token: jkl
  access_token_secret: mno
  consumer_key: pqr
  consumer_secret: sto

```
In order to better enable following many hundreds of Twitter acounts, `particle` builds a custom Twitter list and then listens for updates. You can build this list by providing three parameters: the name of the Twitter handle associated with your API keys, the name of the list you want to build, and a list of the screen names you want to follow. In `particle.yml` this looks like this:
```
  list_owner: brianabelson
  list_slug: pardata-test
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
  access_token: jkl
  access_token_secret: mno
  consumer_key: pqr
  consumer_secret: sto
  list_owner: brianabelson
  list_slug: pardata-test
  list_screen_names:
  - nytimes
  - nytimesworld
```

#### Facebook



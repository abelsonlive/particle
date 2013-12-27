Configuration
=============

**particle** runs off of a ``yaml`` or ``json`` config file (or simply a ``python`` dictionary) which contains information about the data sources you want to collect. We'll go through the construction of such a file step-by-step. However, if you want to see an example first, check out `this one <http://github.com/abelsonlive/particle/blob/master/examples/nytimes/nytimes.yml>`_.

Global settings
--------------

URLs
~~~~~~~~~~~~~~

``particle`` tries really hard to find specific links around the web. You can set the patterns of these links in the configuration file (referred to as ``particle.yml`` from here on)::

  global:
    content_regexes:
    - .*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*
    short_regexes:
    - nyti\.ms/\w+

``content_regexes`` represents a list of regular expressions you want to use to detect links to content. In this case, I've written a regular expression that will find links to New York Times content::

  content_regexes:
  - .*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*

This list can be as long or as short as you'd like. For instance::

  content_regexes:
  - .*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*
  - .*propublica.org/[a-z]+/[a-z0-9/-]+

``short_regexes`` represents a list of regular expressions you want to use to detect shortened links to content - they usually show up on Facebook and Twitter.  ``particle`` will then unshorten these links so that you can resolve them with regular links::

  short_regexes:
  - nyti\.ms/\w+

Time
~~~~~~~~~~~~~~

``particle`` unionizes these URLs in time, so you don't have to join all the data together yourself. It does this by taking in an arbitrary ``bucket`` parameter representing the number of minutes you'd like to round timestamps down to. This value should correspond to how often you run ``particle`` on a ``cron``. Don't worry though, ``particle`` will still retain the raw timestamp in case you want study the dynamics of more granular events. In addition, ``particle`` will also resolve all UTC timestamps to the local time zone where your content is published or promoted. In ``particle.yml`` this looks like::

  global:
    bucket: 10
    newsroom_timezone: America/New_York

PhantomJS
~~~~~~~~~~~~~~

Finally, in order to properly spin up multiple threads of ``phantomjs``, ``particle`` needs to know where the executable is located.  You can usually locate this by running:

.. code-block:: bash
  
  which phantomjs


Putting it all together, your ``global`` settings should look something like this::

  global:
    bucket: 10
    newsroom_timezone: America/New_York
    phantomjs: /usr/local/bin/phantomjs
    content_regexes:
    - .*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*
    short_regexes:
    - nyti\.ms/\w+

Data Sources
--------------

``particle`` currently supports collection from four data sources:
  * Twitter
  * Facebook
  * RSS Feeds
  * Web Pages (we'll call them 'Promopages' below)

Let's go through each of these and discuss how to customize your ``particle`` project to your needs.

Twitter
~~~~~~~~~~~~~~

Authentication
^^^^^^^^^^^^^^^

``particle`` follows an arbitrary list of Twitter accounts and detects when relevant links are shared. To set this up, you'll first have to `register an app with Twitter <http://dev.twitter.com>`_ and obtain a set of API keys. Once you have these keys, you can enter them into `particle.yml` like so::

  twitter:
    access_token: xxx
    access_token_secret: xxx
    consumer_key: xxx
    consumer_secret: xxx

Data
^^^^^^^^^^^^^^^

In order to better enable following many hundreds of Twitter acounts, ``particle`` builds a custom Twitter list and then listens for updates. You can build this list by providing three parameters: the screen name associated with your API keys, the name of the list you want to build, and a list of the screen names you want to follow. This list is built (or updatated) when you initialize a new Particle object. In `particle.yml` this looks like this::

  lists:
    nytimes-twitter-accounts:
      owner: brianabelson
      screen_names: 
        - nytimes
        - nytimesworld

You can also indicate a path to a textfile of twitter screen names and/or user ids::

  lists:
    nytimes-twitter-accounts:
      owner: brianabelson
      screen_names: screen_names.txt

These lists can also be ones you don't own.  In these cases, you don't need to bother listing any screen names. For instance::

  lists:
    members-of-congress:
      owner: cspan

You can also set the maximum number of of posts to search through at any given time. Currently the maximum is 200. However, so long as you regularly poll Twitter, you can be relatively certain that you won't miss any tweets. You can set this value in ``particle.yml`` like so::

  limit: 200
 
Putting it all together, your ``twitter`` settings might look something like this::

  twitter:
    access_token: xxx
    access_token_secret: xxx
    consumer_key: xxx
    consumer_secret: xxx
    lists:
      nytimes-twitter-accounts:
        limit: 200
        owner: brianabelson
        screen_names: nytimes_twitter.txt
      members-of-congress:
        limit: 200
        owner: cspan

Facebook
~~~~~~~~~~~~~~

Authentication
^^^^^^^^^^^^^^^

As with Twitter, you'll need to register an app with Facebook to access their data. You can do that `here <https://developers.facebook.com/apps>`_::

  facebook:
    app_id: xxx
    app_secret: xxx
    temp_access_token: xxx

One annoyting thing about the Facebook API is that it requires you to hit a particular endpoint to register a stable access token, or an API key that lasts more than a couple of hours. ``particle`` helps solve this by generating a stable access token for you. However, you'll first need a temporary access token - ``temp_access_token`` above. You can obtain one of these by going to `their API explorer <https://developers.facebook.com/tools>`_. Make sure you are using it with the app credentials you've registered above. You can then press "Get Access Token" and copy that string into ``particle.yml``. Now when you initialize a new ``Particle`` object, a stable access token will be generated using your temporary access token and insterted into ``particle.yml``::

  facebook:
    app_id: xxx
    app_secret: xxx
    temp_access_token: xxx
    stable_access_token: xxx
    stable_access_token_expires_at: 0123456789

Here, ``stable_access_token_expires_at`` connotes the time at which this so-called "stable" access token will expire - usually about three months.  However, if you simply remove ``stable_access_token`` from ``particle.yml``. regenerate a temporary access token, and re-run your script, ``particle`` will create a new stable access token for you.

Data
^^^^^^^^^^^^^^^

``particle`` collects information about posts on particular Facebook pages. As with Twitter, it does this by following a list of page slugs::

  pages:
  - nytimes
  - modernlove

Once again, you can specify the number of posts to look through for each user name, now called ``page_limit`` (you'll see why, below)::

  page_limit: 10
a
In addition, if you have access to `Facebook Insights <https://www.facebook.com/help/search/?q=insights>`_ for a set of pages, ``particle`` can grab highly detailed information about how people engaged with posts on these pages over time. You can specify this in ``particle.yml`` as follows::

  insights_pages:
  - nytimes

In this case, you'll want to set the limit (x) according to the number of posts you'd like to track at any one time.  In this logic, when a post first goes live, it will be tracked until x more posts have been published.  Usually I just leave this at it's maximum: 200::

  insights_limit: 200

Putting it all together, your ``facebook`` settings might look something like this::

  facebook:
    app_id: xxx
    app_secret: xxx
    temp_access_token: xxx
    stable_access_token: xxx
    stable_access_token_expires_at: 0123456789
    pages:
    - nytimes
    - modernlove
    page_limit: 10
    insights_pages:
    - nytimes 
    insights_limit: 200

Promopages
~~~~~~~~~~~~~~

A powerful feature of ``particle`` is its ability to pull in links from arbitrary pages and extract metadata about those links, like their position, font size,  associated text, and image attributes. This feature works by harnessing ``phantomjs`` and ``selenium`` to render the pages in a headless browser and scan the links to match the specified url patterns. You can use it to detect links on homepages or really any other site around the web. This function is simply customized in ``particle.yml``::

  promopages:
    nyt_homepage: http://www.nytimes.com/

Here the key of the promopage - ``nyt_homepage`` - indicates how the datastore will refer to an event on this page (more on this below) and the value is the url you want to scan for links.

RSS Feeds
~~~~~~~~~~~~~~

Finally, ``particle`` also allows you to pull in content from abrtrary RSS feeds. Similar to ``promopages``, you set these in ``particle.yml`` by listing key-value pairs that correspond to the name of the feed and the url of the feed. In this case, however, the value consists of two parameters: ``feed_url`` - the url of the feed - and ``full_text`` which takes a boolean value that indicates whether or not the feed contains the full text of the articles. If ``full_text`` is set to "false", ``particle`` will attempt to scrape the article text using a combination of `boilerpipe <https://code.google.com/p/boilerpipe/>`_ and `readability <https://github.com/buriy/python-readability>`_. Here's all that in ``particle.yml``::

  nyt_timeswire:
    feed_url: http://www.nytimes.com/timeswire/feeds/
    full_text: false

Sample Config File
~~~~~~~~~~~~~~

Here's what a sample ``particle.yml`` file looks like::

  global:
    bucket: 10
    newsroom_timezone: America/New_York
    phantomjs: /usr/local/bin/phantomjs
    content_regexes:
    - .*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*
    short_regexes:
    - nyti\.ms/\w+

  facebook:
    app_id: abc
    app_secret: def
    temp_access_token: ghi
    insights_pages:
    - nytimes
    insights_limit: 200
    page_limit: 10
    pages:
    - DealBook
    - modernlove
    - NYTDesign
    - nytimes
    - nytimescivilwar
    - nytimesdining
    - nytimesgiving
    - nytimeslearning
    - nytimesmovies
    - nytimesphoto
    - nytimespolitics
    - nytimesscience
    - nytimestheater
    - nytimesthechoice
    - nytimestravel
    - NYTMetro
    - nytscoop
    - nyttravelshow
    - RoomforDebate
    - TimesOpen
    - timestalks
    - tmagazine
    - WellNYT

  twitter:
    access_token: jkl
    access_token_secret: mno
    consumer_key: pqr
    consumer_secret: sto
    lists:
      nytimes-twitter-accounts:
        limit: 200
        owner: brianabelson
        screen_names: nyt_twitter.txt
      members-of-congress:
        limit: 200
        owner: cspan

  promopages:
    nyt_homepage: http://www.nytimes.com/
    nyt_mobile: http://mobile.nytimes.com/
    nyt_most_emailed: http://www.nytimes.com/most-popular-emailed

  rssfeeds:
    nyt_timeswire:
      feed_url: http://www.nytimes.com/timeswire/feeds/
      full_text: false


Database
--------------

The data is stored in ``redis`` as a sorted set in which the keys are resolved article urls, the rank is the bucketed timestamp, and the value is a json string, with the key of the string signifying the data source and the value connoting the data associated with that event. This means you can quickly get all the events (or just a specific set of events) for a url at a particular time, within a set timerange, or across the entire span of the data without doing any joins.

Read more about how to access the data in the `API documentation <web-api.html>`_.
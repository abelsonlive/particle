.. particle documentation master file, created by
   sphinx-quickstart on Wed Dec 25 21:19:20 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**particle**: track article promotion
========

**particle** is a tool for collecting data about the promotion of articles on Twitter, Facebook, Webpages, and RSS feeds (for now). It automatically joins this data together by a common url and bucketed timestamp.  This enables analysis similar to that which I discuss in this `blog post <http://brianabelson.com/open-news/2013/11/14/Pageviews-above-replacement.html>`_. **particle** is the ideal companion to `pollster <https://github.com/stdbrouw/pollster>`_, which tracks the performance of links on social media.

Quickstart
----------

## Configuration

`particle` runs off of a ``yaml`` or ``json`` config file (or simply a ``python`` dict) which contains information about the data sources you want to collect, referred to here as `particle.yml`. If you want to see an example of such a file, check out [this one](http://github.com/abelsonlive/particle/examples/nytimes/nytimes.yml), though we'll discuss it in more detail below.

When you start a new `particle` project, you'll want to tell `particle` where this file is:
```
from particle import Particle

p = Particle('particle.yml')
```
This one function will read in your configuration file, set it as an environmental variable (`PARTICLE_CONFIG_PATH`), build a Twitter list of the the handles you want to follow, and insert a stable facebook API key (more on all this below).

Now you're all set to run `particle`:
```
p.run(tasks=['twitter', 'facebook'])
```


Contents
--------

.. toctree::
   :maxdepth: 2

   install
   config
   web-api


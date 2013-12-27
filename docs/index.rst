.. particle documentation master file, created by
   sphinx-quickstart on Wed Dec 25 21:19:20 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**particle**: track article promotion
========

**particle** is a tool for collecting data about the promotion of articles on **Twitter**, **Facebook**, **Webpages**, and **RSS feeds** (for now). It automatically joins this data together by a common url and bucketed timestamp.  This enables analysis similar to that which I discuss in this `blog post <http://brianabelson.com/open-news/2013/11/14/Pageviews-above-replacement.html>`_. ``particle`` is the ideal companion to `pollster <https://github.com/stdbrouw/pollster>`_, which tracks the performance of links on social media.

Quickstart
----------

**particle** runs off of a ``yaml`` or ``json`` config file (or simply a ``python`` dictionary) which contains information about the data sources you want to collect. If you want to see an example of such a file, check out `this one <http://github.com/abelsonlive/particle/blob/master/examples/nytimes/nytimes.yml>`_, or go straight to the `configuration documentation <config.html>`_.

When you start a new ``particle`` project, you'll want to indicate where this file is::

  from particle import Particle

  p = Particle('particle.yml')

This one function will set up your ``particle`` project and deal with any necessary authentication with external API's (more on all this in the `configuration documentation <config.html>`_.

Now you're all set to run ``particle``::

  p.run(tasks=['twitter', 'facebook', 'promopages', 'rssfeeds'])

Alternatively, you can run this same sequence of functions via the command line interface:

.. code-block:: bash
  
  $ particle run -c particle.yml

Now put ``particle`` on a ``cron`` and let it go!

.. code-block:: bash

  */10 * * * * cd path/to/particle/project/ && particle run -c particle.yml

Quickstart
----------

You can check out some simple examples in the `github repository <https://github.com/abelsonlive/particle/tree/master/examples>`_.


Contents
--------

.. toctree::
   :maxdepth: 2

   install
   config
   web-api


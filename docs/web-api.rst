
Web API documentation
=================

Endpoints
---------

``particle`` comes with a flexible ``flask`` API for serving the data it captures.  There are two endpoints:

  * Query
  * Recent Articles

You can start up this API like so::

  import particle

  particle.api(port=8000 debug=True)

Or alternatively via the command line interface:

.. code-block:: bash

  $ particle web -p 8000 -d True

Query
~~~~~~~~
<api-url>/recent-articles/<key-value pairs>

``particle`` comes with a flexible endpoint for querying the data by a given url.  Here are the parameters:

  * url (required)
    - The URL of the article you're interested in.
  * data_sources
    - ``twitter_<screen_name>``, ``facebook_<screen_name>``, ``facebook_insights_<screen_name> ``rssfeeds``, or ``promopages``
  * start
    -
  * end 
    -
  * timestamp
    -
  * order
    -
  * include_article
    - Whether or not to include the arti
  * include_keys
    -


Recent Articles
~~~~~~~~~~~~~~~
<api-url>/recent-articles/<key-value pairs>

``particle`` includes an endpoint for tracking the most recent articles to have entered the database.  This is ideal for pairing with `pollster <http://github.com/stdbrouw/pollster>`_.

  * limit
    -
  
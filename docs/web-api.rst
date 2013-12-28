
Command Line Interface
=================

Starting the API
----------------

``particle`` comes with a flexible ``flask`` API for serving the data it captures.

You can start up this API like so::

  import particle

  particle.api(port=8000 debug=True)

Or alternatively via the command line interface:

.. code-block:: bash

  $ particle api -p 8000 -d True

Endpoints
---------

Query
~~~~~~~~
**<api-url>/<key-value pairs>**

``particle`` comes with a flexible endpoint for querying the data by a given url.  Here are the parameters:

  * ``url`` (required)
    - The URL of the article you're interested in.
  * ``data_sources``
    - A comma-seprated list of the following values:
      - ``twitter_<screen_name>``
      - ``facebook_<page_id>``
      - ``facebook_insights_<page_id>`` 
      - ``<rss_feed_name>``
      - ``<promopage_name>``
    - In addition, you can simply use "``twitter``" or "``facebook``" and return all the sources that contain those strings.
  * ``start``
    - A unix timestamp connoting the start of the range of events to search for.
  * ``end``
    - A unix timestamp connoting the end of the range of events to search for.
  * ``timestamp``
    - A unix timestamp connoting the specific time window of events.
  * ``order``
    - What direction to sort the events: ``asc`` or ``desc``
  * ``include_article``
    - Whether or not to include the article data obtained from ``rssfeeds``.
  * ``include_keys``
    - Whether or not to include the data_source names as keys of each event (usually only advisable if you're querying for one data source).

A sample datum might look like this::

  {
      "article": {
          "nyt_timeswire": {
              "rss_raw_link": "http://www.nytimes.com/2013/12/27/us/as-food-programs-are-cut-deer-hunters-share-the-bounty.html?_r=0",
              "rss_title": "As Food Programs Are Cut, Deer Hunters Share the Bounty",
              "rss_pub_date": null,
              "time_bucket": 1388117400,
              "extracted_title": "As Food Programs Are Cut, Deer Hunters Share the Bounty",
              "article_url": "http://www.nytimes.com/2013/12/27/us/as-food-programs-are-cut-deer-hunters-share-the-bounty.html",
              "extracted_content": "Try a Digital Subscription Today for Just 99¢ for Your First 4 Weeks\nGet unlimited access to NYTimes.com and NYTimes apps.\n \nGet 50% Off 12 Weeks of Home Delivery and Free All Digital Access\n \nAs Food Programs Are Cut, Deer Hunters Share the Bounty\nLeslie Boorhem-Stephenson for The Texas Tribune\nHill Country Fine Meats & Fresh Seafood in Marble Falls processes deer donated by Hunters for the Hungry and takes the meat to a food pantry.\nBy EDGAR WALTERS\nPublished: December 26, 2013\nFor hunters like Rick Prekup, deer season is the happiest time of the year.\nExpanded coverage of Texas is produced by The Texas Tribune, a nonprofit news organization. To join the conversation about this article, go to texastribune.org.\n“I go hunting every chance I get,” Mr. Prekup said in a telephone interview from his home in Horseshoe Bay. Several times each week from November to early January, he rises at 5 a.m., grabs his lucky sweater and a semiautomatic Remington rifle and drives about an hour to his hunting lease in Mason County.\nMr. Prekup, who is allowed to shoot up to five deer a year under Texas Parks and Wildlife regulations, generally ends up with more venison than he needs. So he donates a deer or two to the Texas Hunters for the Hungry program, which this year was adopted and expanded by the Texas Food Bank Network to provide hunger relief to needy Texans. He calls the program a way to share the “bounty of Texas.”\n“I like doing it,” Mr. Prekup said. “It’s important for someone to give back if they’re blessed with the ability to go out and hunt.”\nThe start of this year’s deer season on Nov. 2 coincided with a cut to the federal Supplemental Nutrition Assistance Program, formerly known as the food stamp program. Celia Cole, chief executive of the Texas Food Bank Network, said that those cuts had left millions of Texans scrounging for new sources of nutrition and that food banks had struggled to keep up.\n“We see a spike for demand during the holidays,” Ms. Cole said. “The cut to SNAP came at a particularly bad time.”\nThe Hunters for the Hungry program will help offset some of the losses, Ms. Cole said, by providing needy families with a source of protein, often the most expensive part of their diet.\n“One of the things that’s least often donated and is hardest to acquire is that source of low-fat protein,” she said.\nCharlie Ward, chief operating officer of the Capital Area Food Bank of Texas, agreed, saying that local pantries demanded protein-rich foods more than any other types and that venison was particularly popular.\n“When we put it in inventory here, it doesn’t last but a day,” he said.\nIn some communities, participation in the program is widespread. Horseshoe Bay has a deer overpopulation problem, said Stan Farmer, the city manager. To deal with it, the city hires a trapper each year to catch roughly 300 deer, which are processed and donated to Hunters for the Hungry.\nIn addition to contributing to a good cause, Mr. Farmer said, the program manages the community’s deer population. “Otherwise we’ll have maybe 500 deer per year get hit by cars, which is dangerous for drivers and dangerous for deer,” he said.\nBut overall venison donations are inconsistent from year to year, Mr. Ward said. In 2011, his food bank, which serves 21 counties in Central Texas, received more than 8,000 pounds of meat donated by hunters; in 2012, that number fell to just under 2,000 pounds. Mr. Ward said the processing fee — hunters pay an average of $40 per deer — could be a hurdle to donations.\nMs. Cole emphasized that charitable initiatives, while important, could not make up for the federal cuts anyway. November cuts to SNAP eliminated $36 of assistance a month for an average family, which Ms. Cole said amounted to a reduction in roughly 180 million meals in Texas a year. By comparison, Ms. Cole said, the entire Texas Food Bank Network provides about 250 million meals each year.\n“We can’t expect programs like Hunters for the Hungry to solve the problem,” she said.\newalters@texastribune.org\nA version of this article appears in print on December 27, 2013, on page AX of the National edition with the headline: As Food Programs Are Cut, Deer Hunters Share the Bounty .\n",
              "rss_content": "With recent cuts to the federal Supplemental Nutrition Assistance Program, the contributions of hunters to a food program are needed more than ever by Texas food banks.",
              "article_slug": "2013-12-27-us-as-food-programs-are-cut-deer-hunters-share-the-bounty",
              "raw_timestamp": 1388117613
          }
      },
      "events": [
          {
              "nyt_homepage": {
                  "pp_promo_url": "http://www.nytimes.com/",
                  "time_bucket": 1388117400,
                  "pp_font_size": 12,
                  "pp_pos_x": 634,
                  "pp_pos_y": 2509,
                  "pp_headline": "As Food Programs Are Cut, Deer Hunters Share the Bounty",
                  "article_url": "http://www.nytimes.com/2013/12/27/us/as-food-programs-are-cut-deer-hunters-share-the-bounty.html",
                  "raw_timestamp": 1388107024,
                  "pp_link_url": "http://www.nytimes.com/2013/12/27/us/as-food-programs-are-cut-deer-hunters-share-the-bounty.html?src=twrhp",
                  "article_slug": "2013-12-27-us-as-food-programs-are-cut-deer-hunters-share-the-bounty",
                  "pp_is_img": 0
              }
          }
      ]
  }


Recent Articles
~~~~~~~~~~~~~~~
**<api-url>/recent-articles/<key-value pairs>**

``particle`` includes an endpoint for tracking the most recent articles to have entered the database.  This is ideal for pairing with `pollster <http://github.com/stdbrouw/pollster>`_.

  * ``limit``
    - how many articles to return (default = 50)
  
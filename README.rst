scrapyduler
===========

Scrapyd launcher module that schedules scrapy spiders by time.

Install
-------

.. code-block:: shell

    $ pip install scrapyduler

Config
------

To start using this library you just need to override
the ``launcher`` option in your ``scrapyd.conf`` file:

.. code-block:: text

    [scrapyd]
    launcher = scrapyduler.launcher.Launcher

and then add the schedulers configuration, e.g.:

.. code-block:: text

    [scheduler.1]
    cron        = * * * * *
    project     = quotesbot
    spider      = toscrape-xpath
    settings    = HTTPPROXY_ENABLED=True
    args        = key1=value1 key2=value2 start_url=http://quotes.toscrape.com/

    [scheduler.2]
    interval    = weeks=0 days=0 hours=0 minutes=0 seconds=30
    project     = quotesbot
    spider      = toscrape-css
    settings    = HTTPPROXY_ENABLED=True
    args        = key1=value1 key2=value2 start_url=http://quotes.toscrape.com/

In the examples above, we set up two schedulers.
The first scheduler uses cron syntax to run spiders.
The second scheduler triggers on specified intervals,
starting on ``start_date`` if specified, ``datetime.now()`` + interval otherwise.
See https://github.com/agronholm/apscheduler for more information.

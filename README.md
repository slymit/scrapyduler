# scrapyduler

[![version](https://img.shields.io/pypi/v/scrapyduler.svg)](https://pypi.python.org/pypi/scrapyduler)
[![pyversions](https://img.shields.io/pypi/pyversions/scrapyduler.svg)](https://pypi.python.org/pypi/scrapyduler)
[![actions](https://github.com/slymit/scrapyduler/actions/workflows/python-test.yml/badge.svg)](https://github.com/slymit/scrapyduler/actions/workflows/python-test.yml)
[![codecov](https://codecov.io/github/slymit/scrapyduler/graph/badge.svg?token=H1SMMJ0JZ7)](https://codecov.io/github/slymit/scrapyduler)

Scrapyd launcher module that schedules scrapy spiders by time.

## Install

```shell
pip install scrapyduler
```

## Config

To start using this library you just need to override
the `launcher` option in your `scrapyd.conf` file:

```ini
[scrapyd]
launcher = scrapyduler.launcher.Launcher
```

and then add the schedulers configuration, e.g.:

```ini
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
```

In the examples above, we set up two schedulers.
The first scheduler uses cron syntax to run spiders.
The second scheduler triggers on specified intervals,
starting on `start_date` if specified, `datetime.now()` + interval otherwise.
See <https://github.com/agronholm/apscheduler> for more information.

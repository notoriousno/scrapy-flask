
# WSGI and Scrapy

A common question on Scrapy Stackoverflow is "How to use Scrapy with Flask, Django, or any other Python web framework?"
Most are used to using the Scrapy's generated projects and cli options, which make crawling a breeze, but are confused when trying to integrate Scrapy into a WSGI web framework.
A common traceback encountered is `ReactorNotRestartable`, which stems from the underlaying [Twisted](http://twistedmatrix.com/) framework.
This occurs because, unlike asyncio or Tornado, Twisted's eventloop/reactor cannot be restarted once stopped (the reason is a bit out of scope).
So it becomes apparent that the trick to integrating Scrapy and WSGI frameworks involves being able to tame Twisted.
Luckily, integrating async Twisted code with synchronous code has become quite easy and is only getting easier.
In this post, the following will be demonstrated:

* Embed a crawler in a WSGI app and run it using Twisted's `twist web` WSGI server.
* Embed a crawler in a WSGI app and run it any WSGI server (example: [`gunicorn`](http://docs.gunicorn.org/en/stable/), [`uwsgi`](http://uwsgi-docs.readthedocs.io/en/latest/), or [`hendrix`](https://github.com/hendrix/hendrix))


## Requirements

* Python 2.7+
* Twisted 17+
* Scrapy 1.4+
* Crochet 1.90+
* Any WSGI compatible web framework (Flask, Django, Bottle, etc)

**Optional Requirements** - *The following packages are used in the examples below, but any WSGI compatible framework and WSGI server are sufficient.*

* Flask
* Gunicorn


## Git Repo

To make life easy, a git repository has been created to provide all the code that will be discussed.

```
git clone https://github.com/notoriousno/scrapy-flask.git
```


## Quote Spider

Let's setup a quick project structure.
This will be a bit different from those accustomed to a traditional Scrapy project structure, but not by much.
First, let's create a file (`quote_scraper.py`) that will hold a spider that scrapes `http://quotes.toscrape.com`.

```
import re
import scrapy

class QuoteSpider(scrapy.Spider):

    name = 'quote'
    start_urls = ['http://quotes.toscrape.com']
    quotation_mark_pattern = re.compile(r'“|”')

    def parse(self, response):
        quotes = response.xpath('//div[@class="quote"]')
        for quote in quotes:
            # extract quote
            quote_text = quote.xpath('.//span[@class="text"]/text()').extract_first()
            quote_text = self.quotation_mark_pattern.sub('', quote_text)

            # extract author
            author = quote.xpath('.//span//small[@class="author"]/text()').extract_first()

            # extract tags
            tags = []
            for tag in quote.xpath('.//div[@class="tags"]//a[@class="tag"]/text()'):
                tags.append(tag.extract())

            # append to list
            # NOTE: quotes_list is passed as a keyword arg in the Flask app
            self.quotes_list.append({
                'quote': quote_text,
                'author': author,
                'tags': tags})

        # if there's next page, scrape it next
        next_page = response.xpath('//nav//ul//li[@class="next"]//@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page)
```

A quick summary of what this spider does:  Scrape quotes.toscrape.com, extract the quote, author, and tags into a dict (`self.quotes_list`) then scrape the next page, if one is available.
For those wondering where `self.quotes_list` came from, it's a keyword arg that gets passed into the spider object (this will be discussed further when a WSGI app is created).
Commonly, stats would be stored in a database, but for demonstration purposes, I'll show you a clever way to use the properties of a list/dict to store values.
`self.quotes_list` will simply be a list that contains relevant data that we will later JSON-ify and return to the end user.


## WSGI Web App

Let's embed `CrawlerRunner` to run the `QuoteSpider`, created in the previous section, within a Flask application (you can use Django, Bottle, Cherrypy, etc. Flask is just very common).
Let's create two endpoints, `/crawl` to actually scrape and `/results` that will provide the results of the scrape.

```
import json
from flask import Flask
from scrapy.crawler import CrawlerRunner
from quote_scraper import QuoteSpider

app = Flask('Scrape With Flask')
crawl_runner = CrawlerRunner()      # requires the Twisted reactor to run
quotes_list = []                    # store quotes
scrape_in_progress = False
scrape_complete = False

@app.route('/crawl')
def crawl_for_quotes():
    """
    Scrape for quotes
    """
    global scrape_in_progress
    global scrape_complete

    if not scrape_in_progress:
        scrape_in_progress = True
        global quotes_list
        # start the crawler and execute a callback when complete
        eventual = crawl_runner.crawl(QuoteSpider, quotes_list=quotes_list)
        eventual.addCallback(finished_scrape)
        return 'SCRAPING'
    elif scrape_complete:
        return 'SCRAPE COMPLETE'
    return 'SCRAPE IN PROGRESS'

@app.route('/results')
def get_results():
    """
    Get the results only if a spider has results
    """
    global scrape_complete
    if scrape_complete:
        return json.dumps(quotes_list)
    return 'Scrape Still Progress'

def finished_scrape(null):
    """
    A callback that is fired after the scrape has completed.
    Set a flag to allow display the results from /results
    """
    global scrape_complete
    scrape_complete = True


if __name__=='__main__':
    from sys import stdout
    from twisted.logger import globalLogBeginner, textFileLogObserver
    from twisted.web import server, wsgi
    from twisted.internet import endpoints, reactor

    # start the logger
    globalLogBeginner.beginLoggingTo([textFileLogObserver(stdout)])

    # start the WSGI server
    root_resource = wsgi.WSGIResource(reactor, reactor.getThreadPool(), app)
    factory = server.Site(root_resource)
    http_server = endpoints.TCP4ServerEndpoint(reactor, 9000)
    http_server.listen(factory)

    # start event loop
    reactor.run()
```

If you were to run this script, a Twisted WSGI server will start and serve the app on `http://localhost:9000`.
For lack of better words, Flask is running within Twisted.
Let's step through the `crawl_for_quotes` function.
If no scraping is taking place, then a crawler is run.
As mentioned before, we're using `CrawlRunner` which allows for spiders to be executed within a Twisted application.
`CrawlRunner` returns a Twisted `Deferred` which just means that it will "eventually" have a result.
A callback is appended to `eventual` which will set the `scrape_complete` flag once the scraping is done.


## Twisted's WSGI Server

For the "pro" users and Twisted BDFL's out there, you can use `twist` to easily spin up WSGI applications with minimal command:

```
PYTHONPATH=$(pwd) twist web --wsgi flask_twisted.app --port tcp:9000:interface=0.0.0.0
```

If this is strange to you or doesn't work, then don't stress it and just run `flask_twisted.py` from the git repo.
I've provided this for anyone that may want an alternative to running the script directly.


## Use Any WSGI Server

Most will want to deploy using a WSGI server like Gunicorn, and for those people `flask_twisted.py` will not work because Twisted needs to be running within the same thread.
Fortunately, there's a great project called [`crochet`](https://crochet.readthedocs.io/en/stable/#) that allows Twisted code to run in a non-async code base.
Without dwelling too much how `crochet` works, let's create a new `flask_crochet.py` file:

```
import crochet
crochet.setup()     # initialize crochet

import json
from flask import Flask
from scrapy.crawler import CrawlerRunner
from quote_scraper import QuoteSpider

app = Flask('Scrape With Flask')
crawl_runner = CrawlerRunner()      # requires the Twisted reactor to run
quotes_list = []                    # store quotes
scrape_in_progress = False
scrape_complete = False

@app.route('/crawl')
def crawl_for_quotes():
    """
    Scrape for quotes
    """
    global scrape_in_progress
    global scrape_complete

    if not scrape_in_progress:
        scrape_in_progress = True
        global quotes_list
        # start the crawler and execute a callback when complete
        scrape_with_crochet(quotes_list)
        return 'SCRAPING'
    elif scrape_complete:
        return 'SCRAPE COMPLETE'
    return 'SCRAPE IN PROGRESS'

@app.route('/results')
def get_results():
    """
    Get the results only if a spider has results
    """
    global scrape_complete
    if scrape_complete:
        return json.dumps(quotes_list)
    return 'Scrape Still Progress'

@crochet.run_in_reactor
def scrape_with_crochet(_list):
    eventual = crawl_runner.crawl(QuoteSpider, quotes_list=_list)
    eventual.addCallback(finished_scrape)

def finished_scrape(null):
    """
    A callback that is fired after the scrape has completed.
    Set a flag to allow display the results from /results
    """
    global scrape_complete
    scrape_complete = True

if __name__=='__main__':
    app.run('0.0.0.0', 9000)
```

`crochet` needs to setup the ideal environment in order to work, so one of the first things developers must do is `crochet.setup()`.
Each function that needs to be run in a Twisted thread must be wrapped with `@crochet.run_in_reactor`.
So the difference between `flask_twisted.py` and `flask_crochet.py` is that `CrawlerRunner` is executed in a Twisted thread.
And although the example doesn't demonstrate this, the crawler can indeed run multiple times, essentially side skirting the `ReactorNotRestartable` dilemma.
Without further ado (*adieu*?), how to run this script in Gunicorn:

```
gunicorn -b 0.0.0.0:9000 flask_crochet:app
```


## Test Endpoints

Initiate scrape
```
curl 127.0.0.1:9000/crawl
# output: SCRAPING
```

Trying to scrape again without completing the first scrape
```
curl 127.0.0.1:9000/crawl
# output: SCRAPING IN PROGRESS
```

Server letting you know the scrape is complete
```
curl 127.0.0.1:9000/crawl
# output: SCRAPE COMPLETE
```

Getting the results
```
curl 127.0.0.1:9000/results
```

Getting pretty results using Python's `json.tool`
```
curl 127.0.0.1:9000/results | python -m json.tool | less
```


## Final Words and Caution

There are many other options to solve the issue of using Scrapy/Twisted and WSGI apps.
This is merely a solution that has worked for me in the past.
It's very simple and easy to get a grasp on.
However, things can quickly get chaotic when threads get involved.
Developers will have to worry about shared variables, critical sections, locks, spawning too many threads, debugging, and a plethora of other nuisances.
Hence why the examples are very basic.
Multithreaded code is difficult, which is why a [Mozilla engineer mandates a height restriction](http://i.imgur.com/lWtloyt.jpg).
I'm planning to demonstrate how to achieve similar results in a single thread using [`klein`](https://github.com/twisted/klein) and [`tornado`](http://www.tornadoweb.org/en/stable/) in the future, so stay tuned!


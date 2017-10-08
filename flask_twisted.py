"""
A Flask web app that scrapes http://quotes.toscrape.com using Scrapy and Twisted.
To run this app, run it directly:

    python flask_twisted.py

Alternatively, use Twisted's `twist` executable. This assumes you're in the directory where the
source files are located:

    PYTHONPATH=$(pwd) twist web --wsgi flask_twisted.app --port tcp:9000:interface=0.0.0.0

"""


import json

from flask import Flask
from scrapy.crawler import CrawlerRunner

from quote_scraper import QuoteSpider


app = Flask('Scrape With Flask')
crawl_runner = CrawlerRunner()      # requires the Twisted reactor to run
quotes_list = []                    # store quotes
scrape_in_progress = False
scrape_complete = False


@app.route('/greeting')
@app.route('/greeting/<name>')
def greeting(name='World'):
    return 'Hello %s!' % (name)

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


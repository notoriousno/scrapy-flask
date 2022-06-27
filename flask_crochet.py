"""
If Twisted's WSGI server is not desired in favor for solutions like uwsgi or gunicorn or anything similar,
the `crochet` library can execute Twisted code in an isolated thread. Be EXTREMELY careful with this solution!
Python's WSGI servers generally use threads, as does `crochet`, and/or processes which means there might be
situations where one thread may spawn multiple threads. It's up to the developers to account for intricacies
hen dealing with multi threaded/process applications.

Local usage:

    python flask_crochet.py

Gunicorn usage:

    gunicorn -b 0.0.0.0:9000 flask_crochet:app

"""
import crochet

crochet.setup()  # initialize crochet

import json

from flask import Flask
from scrapy.crawler import CrawlerRunner

from quote_scraper import QuoteSpider
from Spiders.Immoland_scraper import Immoland_scraper as Immoland_scraper
from Spiders.Affare_scraper import Affare_scraper as Affare_scraper

app = Flask('Scrape With Flask')
crawl_runner = CrawlerRunner()  # requires the Twisted reactor to run
quotes_list = []  # store quotes
scrape_in_progress = False
scrape_complete = False


@app.route('/greeting')
@app.route('/greeting/<name>')
def greeting(name='World'):
    return 'Hello %s!' % (name)


@app.route('/crawl/<scraper_name>')
def crawl_for_quotes(scraper_name="a"):
    """
    Scrape for quotes
    """
    global scrape_in_progress
    global scrape_complete
    scraper_name = scraper_name.lower()

    # get the scraper name from route
    if scraper_name not in ["immoland", "affare"]:
        return "Invalid Scraper Name"

    if not scrape_in_progress:
        scrape_in_progress = True
        global quotes_list
        # start the crawler and execute a callback when complete
        scrape_with_crochet(quotes_list, scraper_name)
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
def scrape_with_crochet(_list, scraper_name):
    # test for the scraper name


    if scraper_name == "immoland":
        eventual = crawl_runner.crawl(Immoland_scraper, quotes_list=_list)
    if scraper_name == "affare":
        eventual = crawl_runner.crawl(Affare_scraper, quotes_list=_list)
    eventual.addCallback(finished_scrape)


def finished_scrape(null):
    """
    """
    global scrape_complete
    scrape_complete = True


if __name__ == '__main__':
    app.run('0.0.0.0', 9000)

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


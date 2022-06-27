import re

import jsonpickle
import scrapy

from Model.RealestateScraperItem import RealestateScraperItem


class QuoteSpider(scrapy.Spider):

    name = 'quote'
    start_urls = ['https://www.immoland.tn/advanced-search/?lat=&lng=&use_radius=on&radius=2&status=a-vendre&type=&bedrooms=&bathrooms=&min-price=&max-price=',]
    quotation_mark_pattern = re.compile(r'“|”')



    def parse(self, response):
        # quotes = response.xpath('//div[@class="quote"]')
        list = response.css('div.item-listing-wrap')

        # for quote in quotes:
        for resource in list:
            item = RealestateScraperItem()
            # extract quote
            item['link'] = resource.css('h2.item-title a::attr(href)').get()
            item['title'] = resource.css('h2.item-title a::text').get()
            item['adresse'] = resource.css("address::text").get()
            item['price'] = resource.css("li.item-price::text").get()
            item['salle_de_bain'] = resource.css("li.h-baths span:nth-child(3)::text").get()
            item['nbpiece'] = resource.css("li.h-beds span:nth-child(3)::text").get()
            item['typeImm'] = resource.css("li.h-type span::text").get()
            item['agence'] = resource.css("div.item-author a::text").get()



            # append to list
            # NOTE: quotes_list is passed as a keyword arg in the Flask app

            self.quotes_list.append({
                "link" : item['link'],
                "title": item['title'] ,
                "adresse":item['adresse'],
                "price":item['price'] ,
                "salle_de_salle_de_bain":item['salle_de_bain'],
                "nbpiece":item['nbpiece'],
                "typeImm":item['typeImm'],
                "agence":item['agence']
            })

        # if there's next page, scrape it next
        next_page = response.css("ul.pagination.justify-content-center li:nth-last-child(2) a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page)

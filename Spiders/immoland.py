import scrapy

from Model.RealestateScraperItem import RealestateScraperItem


class Spider(scrapy.Spider):
    name = 'immoLandSpider'
    start_urls = [
        'https://www.immoland.tn/advanced-search/?lat=&lng=&use_radius=on&radius=2&status=a-vendre&type=&bedrooms=&bathrooms=&min-price=&max-price=',
        ]

    def parse(self, response):
        list = response.css('div.item-listing-wrap')

        for resource in list:
            item = RealestateScraperItem()
            item['link'] = resource.css('h2.item-title a::attr(href)').get()
            item['title'] = resource.css('h2.item-title a::text').get()
            item['adresse'] = resource.css("address::text").get()
            item['price'] = resource.css("li.item-price::text").get()
            item['salle_de_bain'] = resource.css("li.h-baths span:nth-child(3)::text").get()
            item['nbpiece'] = resource.css("li.h-beds span:nth-child(3)::text").get()
            item['typeImm'] = resource.css("li.h-type span::text").get()
            item['agence'] = resource.css("div.item-author a::text").get()

            if resource.css("li.h-area span:nth-child(2)::text").get() is not None:
                item['superficie_habitable'] = resource.css("li.h-area span:nth-child(2)::text").get()

            if resource.css("img.img-fluid.wp-post-image::attr(src)").get() is not None:
                item['thumbnail_url'] = resource.css("img.img-fluid.wp-post-image::attr(src)").get()

            yield item
        next_page = response.css("ul.pagination.justify-content-center li:nth-last-child(2) a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

import scrapy

from Model.RealestateScraperItem import RealestateScraperItem


class Spider(scrapy.Spider):
    name = 'quote'
    start_urls = ['https://www.affare.tn/petites-annonces/tunisie/vente-appartement',
                  'https://www.affare.tn/petites-annonces/tunisie/vente-maison',
                  'https://www.affare.tn/petites-annonces/tunisie/terrain'
                  ]
    for i in range(1,250):
        start_urls.append('https://www.affare.tn/petites-annonces/tunisie/vente-appartement?o='+str(i))

    for i in range(1,363):
        start_urls.append('https://www.affare.tn/petites-annonces/tunisie/vente-maison?o='+str(i))

    for i in range(1,376):
        start_urls.append('https://www.affare.tn/petites-annonces/tunisie/terrain?o='+str(i))

    def parse(self, response):
        list = response.css("div.col-xs-12.col-sm-8 div div:nth-child(3) div.AnnoncesList_product_x__BzrCL   ")
        for resource in list:
            item = RealestateScraperItem()
            item['description'] = resource.css("a div:nth-child(2) div::text").get()
            item['price'] = resource.css("span.AnnoncesList_price__J_vIo::text").get()
            item['adresse'] = resource.css("div.AnnoncesList_section7877o__bOPTn div:nth-child(3) p::text").get()
            item['nbpiece'] = resource.css(
                "div.AnnoncesList_section7877o__bOPTn div:nth-child(3) p:nth-child(2) span::text").get()
            item['superficie_habitable'] = resource.css(
                "div.AnnoncesList_section7877o__bOPTn div:nth-child(3) p:nth-child(2) span:nth-child(2)::text").get()
            item['dateAnnonce'] = resource.css(
                "div.AnnoncesList_section7877o__bOPTn div:nth-child(3) p:nth-child(3)::text").get()
            item['link'] = resource.css("a::attr(href)").get()
            item['typeImm'] = None
            item['gouvernorat'] = None
            item['delegation'] = None
            item['localite'] = None
            item['reference'] = None
            item['nbpiece_superficie_habitable'] = None
            item['thumbnail_url'] = None
            item['thumbnail_name'] = None
            item['garage'] = None
            item['agence'] = None
            item['tel'] = None
            item['constructible'] = None
            item['fonds'] = None
            item['installations_sportives'] = None
            item['climatisation'] = None
            item['salle_de_bain'] = None
            item['chauffage'] = None
            item['plein_air'] = None
            item['service'] = None
            item['typeImm'] = None

        self.quotes_list.append({
            "link": item['link'],
            "title": item['title'],
            "adresse": item['adresse'],
            "price": item['price'],
            "salle_de_salle_de_bain": item['salle_de_bain'],
            "nbpiece": item['nbpiece'],
            "typeImm": item['typeImm'],
            "agence": item['agence'],
            "garage": item['garage'],
            "constructible": item['constructible'],
            "fonds": item['fonds'],
            "installations_sportives": item['installations_sportives'],
            "climatisation": item['climatisation'],
            "chauffage": item['chauffage'],
            "plein_air": item['plein_air'],
            "service": item['service'],
            "dateAnnonce": item['dateAnnonce'],
            "thumbnail_url": item['thumbnail_url'],
            "thumbnail_name": item['thumbnail_name'],
            "reference": item['reference'],
            "localite": item['localite'],
            "delegation": item['delegation'],
            "gouvernorat": item['gouvernorat'],
"nbpiece_superficie_habitable": item['nbpiece_superficie_habitable'],
            "description": item['description'],
            "superficie_habitable": item['superficie_habitable']
        })
        next_page = response.css("ul.pagination-lg.pagination li:last-child a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


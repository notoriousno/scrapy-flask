# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RealestateScraperItem(scrapy.Item):
    #default_input_processor = MapCompose(unicode.strip)
    # define the fields for your item here like:
    link=scrapy.Field()#
    title=scrapy.Field()#
    gouvernorat=scrapy.Field()
    delegation=scrapy.Field()
    localite=scrapy.Field()
    codeP=scrapy.Field()
    adresse=scrapy.Field()
    superficie_habitable=scrapy.Field()#
    superficie_terrain=scrapy.Field()#
    nbpiece=scrapy.Field()#
    price=scrapy.Field()#
    anneeConst=scrapy.Field()#
    description=scrapy.Field()#
    typeImm=scrapy.Field()#
    service=scrapy.Field()
    plein_air=scrapy.Field()#
    chauffage=scrapy.Field()
    salle_de_bain=scrapy.Field()#
    climatisation=scrapy.Field()
    cuisine=scrapy.Field()
    installations_sportives=scrapy.Field()
    fonds=scrapy.Field()#
    constructible=scrapy.Field()#
    dateAnnonce=scrapy.Field()
    tel=scrapy.Field()
    agence=scrapy.Field()
    reference=scrapy.Field()
    nbpiece_superficie_habitable = scrapy.Field()
    thumbnail_url = scrapy.Field()
    thumbnail_name = scrapy.Field()
    garage = scrapy.Field()



    

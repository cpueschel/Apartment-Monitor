# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose
from .helpers import clean

class ScrapersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ApartmentItem(scrapy.Item):
    name = scrapy.Field(input_processpor=MapCompose(clean))
    location = scrapy.Field(input_processpor=MapCompose(clean))
    city = scrapy.Field(input_processpor=MapCompose(clean))
    prices = scrapy.Field(input_processpor=MapCompose(clean))
    date = scrapy.Field(input_processpor=MapCompose(clean))

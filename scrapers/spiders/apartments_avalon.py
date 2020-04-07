# -*- coding: utf-8 -*-
import scrapy
import re
import time
import logging
from ..items import ApartmentItem

logger = logging.getLogger(__name__)


class ApartmentsAvalonSpider(scrapy.Spider):
    name = 'apartments_avalon'
    allowed_domains = ['avaloncommunities.com']
    start_urls = ['https://www.avaloncommunities.com/massachusetts']

    locations_interested = [
        'boston',
        'cambridge',
        'somerville',
        'quincy',
        'saugus'
    ]
    def start_requests(self):
        yield scrapy.Request(url=ApartmentsAvalonSpider.start_urls[0], callback=self.parse_main_listings)

    def parse_main_listings(self, response):
        date = time.time()
        logger.debug(f"Starting at date={date}")

        for listing in response.xpath('//li[@class="community-item"]'):
            listing_items = {
                'name': listing.xpath('.//h2[@class="title"]//text()').get(),
                'location': listing.xpath('.//div[@class="address"]//text()').get(),
                'city': listing.xpath('.//div[@class="address"]//text()').get().split(',')[0].split(' ')[-1],
                'date' : date
            }
            logger.debug(f"Got listing for name={listing_items['name']} in the city of {listing_items['city']}")

            prices = []
            raw_prices = listing.xpath('.//div[@class="bottom-content"]//span//text()').getall()
            for raw_prices in raw_prices:
                price = get_dollar_str_from_str(raw_prices)
                apartment_type = raw_prices.split('from')[0]
                if apartment_type is not None and price is not None and apartment_type != 'furnished':
                    prices.append({
                        'price': price.replace('$', ''),
                        'apartment_type': apartment_type.strip().lower()
                    })
            listing_items['prices'] = prices
            logger.debug(f"Found the following prices of {listing_items['prices']}")

            if listing_items['city'].lower() in self.locations_interested:
                yield ApartmentItem(listing_items)



def get_dollar_str_from_str(text: str) -> str or None:
    pattern = r'\$\d+(,\d{3})*(\.[0-9]*)?'
    result = re.search(pattern, text)
    if result:
        dollar = result.group(0)
        return dollar.replace(',', '').replace('$', '')

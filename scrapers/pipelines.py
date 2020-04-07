# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from .database_helpers import insert_values, get_id_where


class ScrapersPipeline(object):
    def process_item(self, item, spider):
        return item


class ApartmentPipeline(object):

    def process_item(self, item, spider):
        if item.get('name') and item.get('city') and item.get('date') and item.get('prices'):
            apartment_id = get_id_where(table_name='apartment',
                                        values={'name': item.get('name'), 'city': item.get('city')})

            if apartment_id is None:
                values = f"\'{item.get('name')}\', \'{item.get('location')}\', \'{item.get('city')}\'"
                insert_values(table_name='apartment', values_string=values)
                apartment_id = get_id_where(table_name='apartment',
                                            values={'name': item.get('name'), 'city': item.get('city')})

            # Add new values to the database
            for price in item.get('prices'):
                values = f"{int(apartment_id)}, {int(price['price'])}, \'{price['apartment_type']}\', {int(item.get('date'))}"
                insert_values(table_name='prices', values_string=values)
            else:
                raise DropItem(f"Missing information for the item={item}")

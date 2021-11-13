# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import json


class GenericItem(scrapy.Item):
    content_type = scrapy.Field()       # string
    series_name = scrapy.Field()        # string
    savepath = scrapy.Field()           # string
    chapter_id = scrapy.Field()         # integer
    chapter_name = scrapy.Field()       # string
    chapter_content = scrapy.Field()    # list of strings

    def __repr__(self):
        return json.dumps({"content_type": self['content_type'], "series_name": self['series_name'], "chapter_id":self['chapter_id'], "chapter_name":self['chapter_name']},indent=2)

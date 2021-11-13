# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import pdb
from scrapy.exceptions import DropItem

class WatchtowerPipeline:
    def process_item(self, item, spider):
        if item['content_type'] == 'Novel':
            obj = Novel()
        elif item['content_type'] == 'Comic':
            obj = Comic()
        elif item['content_type'] == 'Video':
            obj = Video()
        else:
            raise Exception('Bad content_type passed in')
        obj.process_item(item, spider)
        return item

class Novel(WatchtowerPipeline):

    def process_item(self, item, spider):
        # start by validating each field
        item["series_name"] = self.validate_string(item["series_name"])
        item["savepath"] = self.validate_string(item["savepath"])
        item["chapter_id"] = self.validate_string(item["chapter_id"])
        item["chapter_name"] = self.validate_string(item["chapter_name"])
        item["chapter_content"] = self.validate_list_of_strings(item["chapter_content"])
        # now save the data
        self.save_data(item)
        # finally, drop this item
        print("Done Processing Item with ID|Name: %s|%s" % (item["chapter_id"], item["chapter_name"]))
        #raise DropItem("Done Processing Item with ID|Name: %s|%s" % (item["chapter_id"], item["chapter_name"]))
        return item

    def validate_string(self, data):
        if not data:
            raise Exception('Should never be empty')
        return data

    def validate_list_of_strings(self, data):
        if not data:
            data = []
        return data

    def save_data(self, item):
        folder_dir = os.path.sep.join([item['savepath'], item['series_name'], 'raws'])
        os.makedirs(folder_dir, exist_ok=True)

        # overwrite any existing files with the same names
        filename = '%s%s%s.txt' % (folder_dir, os.path.sep, item['chapter_id'])

        try:
            if os.path.isfile(filename):
                return # this scraped chapter should not overwrite the existing file
            with open(filename, "w", encoding='utf-8') as f:
                content = [item["chapter_name"]] + item["chapter_content"]
                f.writelines([val + '\n' for val in content])
        except:
            pdb.set_trace()

class Comic(WatchtowerPipeline):
    def process_item(self, item, spider):
        return item

class Video(WatchtowerPipeline):
    def process_item(self, item, spider):
        return item

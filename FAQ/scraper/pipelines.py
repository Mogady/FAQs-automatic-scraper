import os
import json

from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter

from .items import FullItem, FAQItem
from ..validators import spider_validator, FAQ_validator
from ..utils.definitions import ROOT_DIR


class DropPipeline:
    def process_item(self, item, spider):
        if type(item) is FullItem:
            try:
                schema_check = spider_validator.validate_doc(dict(item), spider.settings['name'], spider.logger)

            except AttributeError as e:
                raise DropItem("Dropped: spider Company name is not provided")
            if not schema_check:
                raise DropItem("Dropped: Error in Scrapy Json Schema: %s" % item)

            return item
        elif type(item) is FAQItem:
            try:
                schema_check = FAQ_validator.validate_doc(dict(item), spider.settings['name'], spider.logger)

            except AttributeError as e:
                raise DropItem("Dropped: spider Company name is not provided")
            if not schema_check:
                raise DropItem("Dropped: Error in Scrapy Json Schema: %s" % item)

            return item


class LocalWriterPipeline:
    def __init__(self, settings):
        self.company = settings['name']
        self.items = []
        self.output_path = os.path.join(ROOT_DIR, self.company)
        os.makedirs(os.path.join(ROOT_DIR, self.company), exist_ok=True)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):
        if isinstance(item, FullItem):
            page_name = '/'.join(item['url'].rstrip('/').split('/')[-2:])
            file_path = os.path.join(self.output_path, 'data/' + page_name + '.json')
            with open(file_path, 'w') as fp:
                json.dump(ItemAdapter(item).asdict(), fp)

            return item
        else:
            self.items.append(ItemAdapter(item).asdict())
            return item

    def close_spider(self, spider):
        """
        Callback function when spider is closed.
        """
        if not self.items:
            return  # Do nothing when items is empty.
        file_path = os.path.join(self.output_path, 'Stats.json')
        with open(file_path, 'w') as fp:
            json.dump(ItemAdapter(self.items).asdict(), fp)


class JsonWriterPipeline:
    def __init__(self, settings):
        self.company = settings['name']
        self.items = []
        os.makedirs(os.path.join(ROOT_DIR, self.company), exist_ok=True)
        self.file = open(os.path.join(ROOT_DIR, self.company, 'FAQs.json'), 'w')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item

import scrapy


class FullItem(scrapy.Item):
    """
    Item representing an full html content
    """
    url = scrapy.Field(serializer=str)
    company = scrapy.Field(serializer=str)
    content = scrapy.Field(serializer=str)
    category = scrapy.Field(serializer=str)


class StatsItem(scrapy.Item):
    """
    Item representing an link statistics
    """
    url = scrapy.Field(serializer=str)
    parent = scrapy.Field(serializer=str)
    count = scrapy.Field(serializer=str)


class FAQItem(scrapy.Item):
    """
    Item representing an FAQ extracted from Zendisk
    """
    html_url = scrapy.Field(serializer=str)
    company = scrapy.Field(serializer=str)
    category = scrapy.Field(serializer=str)
    raw_question = scrapy.Field(serializer=str)
    answer = scrapy.Field(serializer=str)
    question = scrapy.Field(serializer=str)
    text = scrapy.Field(serializer=str)

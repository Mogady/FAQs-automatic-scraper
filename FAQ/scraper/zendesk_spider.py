# -*- coding: utf-8 -*-
import json
import scrapy
from urllib.parse import urlparse
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor

from .items import FAQItem
from ..utils.general_utilities import normalize_questions, extract_text


class ZendeskArticlesSpider(scrapy.Spider):
    """
    Base class for help-centers with zendesk API v2 enabled
    """
    name = "zendesk_spider"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened,
                                signal=scrapy.signals.spider_opened)

        return spider

    def spider_opened(self):
        parsed_uri = urlparse(self.settings['HELPCenter'])
        self.company_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        self.company_name = self.settings['name']
        self.start_url = [f'{self.company_domain}/api/v2/help_center/en-us/sections.json',
                          f'{self.company_domain}/api/v2/help_center/en-us/articles.json']
        print(self.start_url)
        self.sections = {}

    def start_requests(self):
        print(self.start_url[0])
        yield scrapy.Request(url=self.start_url[0], callback=self.parse)

    def parse(self, response, **kwargs):
        result = json.loads(response.body_as_unicode())
        if 'articles' in response.url:
            for article in result['articles']:
                yield self.parse_attr(article)
        else:
            for section in result['sections']:
                self.sections[section['id']] = section['name']
        if result['next_page']:
            next_page = result['next_page']
            yield scrapy.Request(next_page, callback=self.parse, meta={"reset_depth": True})
        else:
            yield scrapy.Request(url=self.start_url[1], callback=self.parse)

    def parse_attr(self, article):
        if len(self.sections.keys()) == 0:
            category = 'Others'
        else:
            category = self.sections[article['section_id']]
        item = {'raw_question': article['title'],
                'question': normalize_questions(article['title']),
                'answer': article['body'],
                'text': extract_text(article['body']),
                'html_url': article['html_url'],
                'category': category,
                'company': self.company_name}
        faq = FAQItem(item)

        return faq


def crawl_zendesk(settings, items):
    """
    main function to run scrapy spider
    :param items:
    :param settings: Spider settings
    :return:
    """
    runner = CrawlerRunner(settings)
    for item in items:
        runner.settings['name'] = item[0]
        runner.settings['HELPCenter'] = item[1]
        runner.crawl(ZendeskArticlesSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

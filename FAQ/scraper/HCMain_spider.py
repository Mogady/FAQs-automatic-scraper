# python modules
import re

# scrapy modules
import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.linkextractors import LinkExtractor
from .items import FullItem, StatsItem


class HelpCenterSpider(scrapy.Spider):
    name = "hc_spider"

    def __init__(self):
        super(HelpCenterSpider, self).__init__()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        return spider

    def start_requests(self):
        start_url = self.settings['HELPCenter']
        if isinstance(start_url, list):
            for url in start_url:
                yield scrapy.Request(url=url, callback=self.parse, meta={'help_url': url,
                                                                         'parent_url': url,
                                                                         })
        else:
            yield scrapy.Request(url=start_url, callback=self.parse, meta={'help_url': self.settings['HELPCenter'],
                                                                           'parent_url': self.settings[
                                                                               'HELPCenter'],
                                                                           })

    def parse(self, response, **kwargs):

        extractor = LinkExtractor(unique=True, allow=re.escape(response.meta['parent_url'].rstrip('/') + '/'),
                                  restrict_xpaths='//body/*')
        links = extractor.extract_links(response)
        if response.url.rstrip('/') == response.meta['parent_url'].rstrip('/'):
            stats_item = {
                'url': response.url,
                'parent': 'parent',
                'count': str(len(links)),
            }
        else:
            stats_item = {
                'url': response.url,
                'parent': response.meta['parent_url'],
                'count': str(len(links)),
            }
        content_item = {'url': response.url,
                        'company': self.settings['name'],
                        'content': response.text,
                        }
        yield StatsItem(stats_item)
        yield FullItem(content_item)
        if len(links) <= 200:
            for link in links:
                yield scrapy.Request(url=link.url.rstrip('/'),
                                     callback=self.parse, dont_filter=False,
                                     meta={
                                         'help_url': self.settings['HELPCenter'],
                                         'parent_url': response.url})

        else:
            self.logger.warning("discarding %s : have links more than the current limit", response.url)
            yield None


def crawl_general(settings, items):
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
        runner.crawl(HelpCenterSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

import getopt
import json
import sys
import yaml

from FAQ.scraper.HCMain_spider import crawl_general
from FAQ.scraper.zendesk_spider import crawl_zendesk
from FAQ.utils.definitions import SPIDER_SETTINGS
from FAQ.utils.general_utilities import config_logger


def run(spider_args):
    t = ''
    file_path = ''

    try:
        opts, args = getopt.getopt(spider_args, "t:f:")
    except getopt.GetoptError:
        print('run.py -t operation_type -f filepath')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-t':
            t = arg
        elif opt == '-f':
            file_path = arg

    logger = config_logger('logs', 'scraper')

    with open(SPIDER_SETTINGS, 'r') as stream:
        try:
            settings = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            raise Exception("couldn't load spider settings yaml file")
    if t == 'zendesk':
        crawl_ = crawl_zendesk

    elif t == 'general':
        crawl_ = crawl_general

    else:
        logger.error("no spider type provided, closing program")
        return

    if not file_path:
        logger.error("no file provided for list of companies, closing program")
        return

    list_companies = []
    with open(file_path, 'r') as f:
        reader = json.load(f)

    for item in reader:
        list_companies.append([item['name'], item['help_url']])

    if len(list_companies) > 0:
        logger.info("scraping %s", [x[0] for x in list_companies])
        crawl_(settings, list_companies)

    else:
        logger.warning("No companies to scrap")
        return


if __name__ == "__main__":
    run(sys.argv[1:])

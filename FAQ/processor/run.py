import json
import getopt
import sys
import os

from FAQ.processor.data_extraction import QA
from FAQ.utils.general_utilities import faq_item, config_logger

logger = config_logger('logs', 'scraper')


def extract_article_links(tree):
    """
    extracting article links from parent-child tree , the function simply looking for child url that has never been parent to any other urls

    :param tree: dictionary that holds link-child relation
    :return: list of url that hold the last articles or the FAQs
    """
    parents = [item['parent'] for item in tree]
    children = [item['url'] for item in tree]

    articles_urls = ['/'.join(item.rstrip('/').split('/')[-2:]) for item in children if item not in parents]

    return articles_urls


def extract(company_name):
    """
    extracting QA pairs from article links
    :param company_name:
    :return: list of dictionaries
    """
    try:
        # first extract the article links from all the content stored in S3 for this company
        link_child = json.loads(os.path.join(company_name, 'Stats.json'))
        article_links = extract_article_links(link_child)
        faq_items = []
    except Exception:
        logger.exception("couldn't read company files from AWS")
        return []

    if len(article_links) == 0:
        logger.warning("no article links found to be processed")
        return []

    for link in article_links:
        try:
            # second read the html for those links
            article = json.loads(os.path.join(company_name, 'data/' + link + '.json'))

            logger.info(link)
            logger.info("Extracting")
            # extracting QA pairs or Title body for each link
            companies, urls, categories, questions, cleaned_questions, answers, texts = QA(article['content'],
                                                                                           article['category'],
                                                                                           article['company'],
                                                                                           article['url'])
            logger.info("Processing")

            # assert all lists lengths matches to avoid any miss-match logic error between QA pairs
            if not all(len(lst) == len(questions) for lst in [companies, categories, urls,
                                                              answers, texts,
                                                              cleaned_questions]):
                logger.error('length of processed items is not the same, questions:%s, texts:%s ,'
                             'cleaned_questions:%s',
                             len(questions), len(texts), len(cleaned_questions))

                raise ValueError
            joined_items = list(
                zip(companies, urls, categories, questions, answers, cleaned_questions, texts))
            # convert pairs to rustle item dictionary
            faq_items += [faq_item(item) for item in joined_items]

        except Exception:
            logger.exception("discarding url %s \n", link)
            continue

    return faq_items


def run(operation_type):
    file_path = ''
    try:
        opts, args = getopt.getopt(operation_type, "f:l:")
    except getopt.GetoptError:
        print('run.py -f filename -l yes/no')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-f':
            file_path = arg

    if not file_path:
        logger.warning("no file provided for list of companies, closing program")
        return

    reader = json.loads(file_path)

    for item in reader:
        logger.info(item['name'])
        results = extract(item['name'])
        stats_dic = dict()
        stats_dic['extracted_items'] = len(results)


if __name__ == "__main__":
    run(sys.argv[1:])

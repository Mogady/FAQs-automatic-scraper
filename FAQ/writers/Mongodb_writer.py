import json
import yaml
import os
import logging

from pymongo import MongoClient, InsertOne

from FAQ.utils.definitions import TOKENS_PATH, CONFIG_PATH
from FAQ.validators.FAQ_validator import validate_doc

logger = logging.getLogger('Mongodb')


def db_obj(db_server, db_name):
    """
    get object to mongodb collection
    :param db_server:
    :param db_name:
    :return:
    """
    obj = MongoClient(db_server)
    db = obj[db_name]

    return db


def validate(items, company):
    """
    validate item json schema
    :param items: list of items
    :param company: company name
    :return:
    """
    valid_items = []
    failed_items = []
    for item in items:
        if not validate_doc(item, company):
            logger.warning("Validation failed for question %s url %s company %s",
                           item.get('raw_question'), item.get('html_url'), company)
            failed_items.append(item)
        else:
            valid_items.append(item)
    return valid_items, failed_items


class MongoWriter:
    def __init__(self):
        try:
            tokens = json.load(open(os.path.join(TOKENS_PATH, 'mongodb'), 'r'))
            with open(os.path.join(CONFIG_PATH, 'Mongodb_settings.yaml'), 'r') as stream:
                try:
                    self.settings = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    raise Exception("couldn't load mongo yaml file")
        except Exception:
            raise Exception("couldn't load Mongo files please check token file")
        self.server = "mongodb://{}:{}@{}".format(tokens['user'], tokens['password'], self.settings['server'])
        self.client = db_obj(db_server=self.server, db_name=self.settings['name'])

    def check_duplicate(self, collection):
        """check if the company already exists or not"""
        companies = self.client[collection].distinct('company')
        return list(companies)

    def write(self, items, company):
        """

        :param items: list of items to write to mongodb
        :param company: company name
        :return:
        """
        collection = self.settings['writing_collection']
        if (company in self.check_duplicate(collection)) and (not self.settings['rewrite']):
            logger.warning("Company %s already exist , change 'rewrite' option in mongo setting to overwrite", company)
            return []
        else:
            self.client[collection].delete_many({"company": company})
            valid_items, failed_items = validate(items, company)
            queries = [InsertOne(doc) for doc in valid_items]
            try:
                self.client[collection].bulk_write(queries)
            except Exception:
                logger.exception("writing error , couldn't write %s items to the DB", len(items))
                failed_items += valid_items

            return failed_items

    def read(self, company_name):
        """
        read all data from collection
        :return:
        """
        collection = self.settings['reading_collection']
        items = self.client[collection].find({'company': company_name}, {'_id': 0})
        return list(items)

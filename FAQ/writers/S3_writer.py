import json
import boto3
import os
import logging
import yaml

from FAQ.utils.definitions import TOKENS_PATH, CONFIG_PATH

logger = logging.getLogger('S3Writer')


def aws_client(tokens):
    """
    create s3 resource or client to use
    :param tokens: aws tokens
    :return: s3 client
    """
    s3 = boto3.client('s3', aws_access_key_id=tokens['key_id'], aws_secret_access_key=tokens['access_key'])
    return s3


class AWSWriter:
    def __init__(self):
        self.aws_tokens = json.load(open(os.path.join(TOKENS_PATH, 'AWS'), 'r'))
        with open(os.path.join(CONFIG_PATH, 'AWS_settings.yaml'), 'r') as stream:
            try:
                settings = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise Exception("couldn't load AWS yaml file")
        self.s3 = aws_client(self.aws_tokens)
        self.settings = settings

    def write_logs(self, body, folder, filename):
        """
        write logs to s3 bucket
        :param body: content to write
        :param folder: company name , will be the folder name
        :param filename: file name with extension ex test.json
        :return:
        """
        self.s3.put_object(Body=body.getvalue(), Bucket=self.settings['Bucket'],
                           Key=os.path.join(folder, filename + '.log'))

    def write_json(self, data, folder, filename):
        """
        write json data to s3 bucket
        :param data: data to write
        :param folder: folder name
        :param filename: file name with extension .json
        :return:
        """
        try:
            self.s3.put_object(Body=(bytes(json.dumps(data).encode('UTF-8'))), Bucket=self.settings['Bucket'],
                               Key=os.path.join(folder, filename))
        except Exception:
            logger.exception("error while uploading to S3 bucket")

    def read_items(self, folder, filename):
        """
        read file from s3 bucket
        :param folder: folder name
        :param filename: file with extension
        :return:
        """
        try:
            content_object = self.s3.get_object(Bucket=self.settings['Bucket'], Key=os.path.join(folder, filename))
            file_content = content_object.get('Body').read().decode('utf-8')
            return file_content
        except Exception:
            logger.exception("error while reading file %s to S3 bucket", filename)

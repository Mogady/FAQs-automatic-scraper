from bs4 import BeautifulSoup
from collections import defaultdict
import logging
import io
import re
import os

from FAQ.utils.definitions import ROOT_DIR

transl_table = dict([(ord(x), ord(y)) for x, y in zip(u"‘’´“”–-—", u"'''\"\"---")])
# pre-defined regex
RE_ORDERED_LIST_MATCHER = re.compile(r"\d+\.\s")
RE_UNORDERED_LIST_MATCHER = re.compile(r"[-\*\+]\s")
RE_SPACE = re.compile(r"\s\+")
RE_LINK = re.compile(r"((\[.*?\]) ?(\(.*?\)))|((\[.*?\]):(.*?))")
RE_STRONG = re.compile(r"\*\*((?!\*\*).+?)\*\*|\*\*((?!\*\*).+)")
RE_MD_CHARS_MATCHER_ALL = re.compile(r"([`\*_{}\[\]\(\)#!])")
RE_IMAGES = re.compile(r"<img.*?/>")


def config_logger(folder, file_name):
    """
    configure the logger to write to local file
    :param folder:
    :param file_name:
    :return:
    """
    # logging.basicConfig(level=logging.DEBUG)
    path = os.path.join(ROOT_DIR, folder)
    os.makedirs(path, exist_ok=True)
    logger = logging.getLogger()
    log_stringio = io.StringIO()
    handler = logging.StreamHandler(log_stringio)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.setLevel(logging.WARNING)
    fh = logging.FileHandler(os.path.join(path, file_name+'.log'))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    return logger


def extract_text(body):
    """
    function used to extract clean text from html code
    :param body: html body to extract text from
    :return: extracted text as str
    """
    soup = BeautifulSoup(body, 'html.parser')
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text


def list_duplicates(seq):
    """
    function used to get all the duplicates in a a list
    :param seq: list of items
    :return: list of the indices that holds a duplicate
    """
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    dups_indices = [locs[:-1] for key, locs in tally.items()
                    if len(locs) > 1]
    return [item for sublist in dups_indices for item in sublist]


def faq_item(item):
    """
    convert list of values to dictionary
    :param item: list
    :return: dictionary
    """
    dic = dict()
    dic['company'] = item[0]
    dic['html_url'] = item[1]
    dic['category'] = item[2]
    dic['raw_question'] = item[3]
    dic['answer'] = item[4]
    dic['question'] = item[5]
    dic['text'] = item[6]
    dic['html_snippet'] = item[7]
    dic['text_snippet'] = item[8]
    dic['images'] = item[9]

    return dic


def normalize_questions(question):
    """
    normalize and clean all the question and article titles
    :param question: questions or title to normalize
    :return: string
    """
    try:
        question = question.translate(transl_table)
        question = re.sub(r'\s+', ' ', question).strip()
        question = re.sub(r'\?+', '?', question).strip()
        question = re.sub(r'[\s\(\[\-\_]*FAQ[\)\]\-\_\s]*', '', question).strip()
        question = re.sub(r'^[0-9]{1,2}\s{0,1}[-_.*#,:\>]*\s*', '', question).strip()

        # handle the wrong Capitalization
        c = 0
        for word in question.split():
            if word.isupper():
                c += 1
        if c >= len(question.split()) / 2:
            question = question.capitalize()

        else:
            words = question.split()
            text = []
            for word in words:
                if word.isupper():
                    text.append(word)
                else:
                    text.append(word.lower())

            question = text[0].capitalize() + ' ' + ' '.join(text[1:])

        question = question.strip('!"#$%&\'*+,-./:;<=>@^_`|~')
    except Exception as e:
        print(question, e)
    return question

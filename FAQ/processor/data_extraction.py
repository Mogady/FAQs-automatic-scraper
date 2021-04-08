from bs4 import BeautifulSoup
from FAQ.utils.general_utilities import extract_text, list_duplicates, normalize_questions
import re
from collections import defaultdict
from FAQ.utils import exceptions
import logging

logger = logging.getLogger('Extractor')

# normalize some html punctuations to string punctuations
transl_table = dict([(ord(x), ord(y)) for x, y in zip(u"‘’´“”–-—", u"'''\"\"---")])


def extract_title(html):
    """
    extract the title from html
    :param html:
    :return: title string
    """
    soup = BeautifulSoup(html, 'html5lib')
    title = soup.title
    return extract_text(str(title))


def clean_HTML(html, url):
    """
    clean the HTML from all the extra un needed content
    :param url:
    :param html:
    :return:
    """
    soup = BeautifulSoup(html, "html5lib")  # create a new bs4 object from the html data loaded
    body = soup.body
    for script in body.findAll(["script", "style", "input", "nav", "canvas", "svg",
                                ]):  # remove all javascript and stylesheet code
        script.extract()
    for tag in body():
        for attribute in ["class", "id", "name", "style", "type", "data"]:
            del tag[attribute]

    for script in body.findAll(['span', 'br', 'hr', 'abbr', 'article', 'aside', 'b', 'bdi',
                                'bdo', 'blockquote', 'em', 'i', 'font', "noscript"]):  # unwrap span and br
        script.unwrap()
    html = str(body)
    html = re.sub("(<!--.*?-->)", "", html, flags=re.DOTALL)
    return html


def get_questions(html):
    """
    split the html based on existing questions using regex if exists
    :param html:
    :return: regex groups
    """
    regex = r"(<((?!li|ul|ol|dl|dd|td|th|a)[A-Za-z0-9]+\s*)[^<]*>){0,1}<((?!li|ul|ol|dl|dd|td|th|a)[A-Za-z0-9]+\s*)[^<]*>[\n\s]*([A-Za-z0-9\s!\"#$%&\'()*+,-\.;:\[\]_\`{}/]+?\?){1,2}[\n\s]*</?\3>(/?\2>)?"
    matches = re.finditer(regex, html, re.IGNORECASE | re.MULTILINE)
    groups = []
    for matchNum, match in enumerate(matches, start=1):
        groups.append(match.group())
    return groups


def list_empty_answers(seq):
    """
    get list of indices the have an empty tags
    :param seq: list of html elements
    :return: list on indices hold the empty tags
    """""
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    dups_indices = [locs for key, locs in tally.items()
                    if (key == '') or (len(re.sub('<.*?>', '', key).strip().split()) == 0)]
    return [item for sublist in dups_indices for item in sublist]


def split(body, url):
    """
    extract the FAQs from html body if exist if not return the title and cleaned body
    :param url:
    :param body:
    :return: list of questions , list of answers
    """
    # clean and normalize the html
    try:
        cleaned_body = clean_HTML(body, url)
        normal_body = cleaned_body.translate(transl_table)
        # get the questions
        questions = get_questions(normal_body)
        if len(questions) > 0:
            # split the HTML body on the extracted questions to get the answers
            escapes = [re.escape(q) for q in questions]
            regex = '|'.join(escapes)
            answers = re.split(regex, normal_body)
            # make a QA from the title and the first text before the first question
            if len(answers) > len(questions):
                title = extract_title(body)
                questions.insert(0, title)

            # remove the HTMl tags from the question
            questions = [re.sub('<.*?>', '', q).strip() for q in questions]
            # remove empty answers ''
            empty_answers = list_empty_answers(answers)
            for item in sorted(empty_answers, reverse=True):
                del questions[item]
                del answers[item]

            # remove question/answers duplicates
            for dup in sorted(list_duplicates(questions), reverse=True):
                del questions[dup]
                del answers[dup]

            # merging question that has len <2 like "how to" or too long question  might be regex error
            _2 = [questions.index(q) for q in questions[1:] if (len(q.split()) <= 2) or (len(q.split()) >= 20)]
            for item in _2:
                answers[item] = '\n'.join([questions[item], answers[item]])
                answers[item - 1] = '\n'.join([answers[item - 1], answers[item]])
            for item in sorted(_2, reverse=True):
                del questions[item]
                del answers[item]

        else:
            questions = [extract_title(body)]
            answers = [normal_body]
        if len(questions) != len(answers):
            raise exceptions.ExtractionError
        cleaned_questions = [normalize_questions(q) for q in questions]
        texts = [extract_text(body) for body in answers]
        return questions, cleaned_questions, answers, texts

    except exceptions.ExtractionError:
        logger.error("number of questions != number of answers")
        raise
    except Exception:
        logger.error("couldn't extract QA pairs , error in split Function")
        raise


def QA(body, category, company, url):
    """
    main function to process the html content
    :param body: full html content of page
    :param category: category of article
    :param company: company name
    :param url: url onf the html content
    :return: list of questions, answers, companies, urls, pages, categories
    """
    questions, cleaned_questions, answers, texts = split(body, url)

    # expand the other field to the length of extracted QA pairs
    companies = [company] * max(len(questions), 1)
    urls = [url] * max(len(questions), 1)
    categories = [category] * max(len(questions), 1)
    return companies, urls, categories, questions, cleaned_questions, answers, texts

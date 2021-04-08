# Automatic Scraping project for extracting FAQ and Help center articles

## Introduction
This is an FAQs Automatic scraping from help centers articles
using Scrapy tool, by saying Automatic I mean providing a list of companies and 
their HelpCenter URL, and the scraper will start automatically follow all the internal
articles and extract FAQs as a (Question, Answer) pairs.

I learned a lot while trying to make this, and I'm intending to do an article to explain
some problems you might face while doing this and how I approached it.

## How does it work
currently, there are two types of operations to do in the scraper:
- general: scraping general HelpCenter content.
- zendesk: scraping Zendesk companies.

the scraper read a list of companies and start scraping the info,
it writes to json files, folder for each company.

### Zendesk:
this is straight-forward one , Zendesk simply have a common patter in their URL,
```python
f'{company_domain}/api/v2/help_center/en-us/sections.json',
f'{company_domain}/api/v2/help_center/en-us/articles.json'
```
by simply telling the spider to follow those links you can get all the articles, and their
sections which what I did in zendesk_spider.

### general
this is the tricky one, here the objective is to scrap any other help-center url by
following the tree pattern if exist the tree patter is simply 
start_url>>start_url/categories>>start_url>>category>>article.
to do that I keep recursively following the pattern while being careful, to avoid
hitting urls that are not help-center articles.
after that I store all the html content I get and start processing them as a tree looking
for the last html page that contains the article and extract FAQS from it.

## How to use

to build and run the scraper 
```
docker build -f scraping_docker -t scraper .
docker run scraper -f filename -t operation_type
``` 

to build and run the processor 
```
docker build -f processing_docker -t processor .
docker run processor -f filename -t operation_type
```






 
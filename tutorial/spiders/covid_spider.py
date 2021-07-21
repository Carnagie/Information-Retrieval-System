# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
from newspaper import Article
from scrapy.linkextractors import LinkExtractor

filter_words = ['covid', 'corona', 'korona', 'biontech', 'sinovac', 'kovid']
LIMIT = 1


# Basic function for relevance test.
# Check the title, text and meta keywords of the article object
# that will be assigned by the parse() method
def covid_relevance(article):
    title = article.title
    text = article.text
    keywords = article.meta_keywords
    description = article.meta_description
    for fw in filter_words:
        if (fw in title.lower()) or (fw in text.lower()) or (fw in ' '.join(keywords).lower()) or (
                fw in description.lower()):
            return True
    return False


# Main crawler class
class CovidSpider(scrapy.Spider):
    name = "covids"
    start_urls = [
        'https://www.milliyet.com.tr/galeri/biontech-yan-etkileri-neler-biontech-mi-sinovac-mi-daha-etkili-6553256']

    # Count attribute for counting crawled urls
    def __init__(self):
        self.count = 0

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CovidSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    # To signal the crawler while crawling
    def spider_closed(self, spider):
        print('close spider')

    def parse(self, response):

        # Url of the response
        url = response.request.url
        # Creating Article object
        article = Article('')
        # Setting HTML attribute of the Article object
        article.set_html(response.body)
        # Parsing the HTML
        article.parse()

        # Checking covid relevance
        covid_related = covid_relevance(article)

        # Checking covid relevance & Article language
        if (not covid_related) or article.meta_lang != 'tr':
            return

        self.count += 1

        print(f'[RELEVANCE]:{covid_related} -- [LANG]:{article.meta_lang}')
        print(f'[TITLE]{article.title}')
        print(f'[URL]{url}')
        print(f'[COUNT]{self.count}')
        print('#############################################')

        yield {
            'url': url,
            'title': str(article.title),
            'text': str(article.text).lower(),
            'description': article.meta_description,
            'keywords': article.meta_keywords,
            #'html': article.html
        }

        # Extracting next links
        le = LinkExtractor()
        links = le.extract_links(response)

        for link in links:
            new_url = response.urljoin(link.url)
            try:
                yield scrapy.Request(new_url, callback=self.parse)
            except:
                continue

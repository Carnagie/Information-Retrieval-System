# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
from newspaper import Article
from scrapy.linkextractors import LinkExtractor
import os

title_filter_words = ['covid', 'kovid', 'corona', 'korona', 'biontech',
                      'sinovac', 'kovid', 'virüs', 'virus', 'doz', 'aşı', 'vaka',
                      'pandemi', 'salgın', 'varyant', 'karantina', 'bulaş', 'bağışıklı',
                      'test', 'pozitif', 'negatif', 'izolasyon', 'sokağa çıkma yasağı',
                      'bilim kurulu','who', 'dsö', 'dünya sağlık örgütü', 'antikor', 'sosyal mesafe',
                      'maske', 'taşıyıcı', 'normal', 'wuhan']


content_filter_words = ['covid', 'corona', 'korona', 'biontech', 'sinovac', 'kovid']
LIMIT = 1


# Basic function for relevance test.
# Check the title, text and meta keywords of the article object
# that will be assigned by the parse() method
def covid_relevance(article):
    title = article.title
    text = article.text
    keywords = article.meta_keywords
    description = article.meta_description

    for cfw in content_filter_words:
        if cfw in text.lower():

            for fw in title_filter_words:
                if (fw in title.lower()) or (fw in ' '.join(keywords).lower()) or (fw in description.lower()):
                    return 1  # relevant
            return 2  # not directly relevant, just contains covid keywords

    for cfw in content_filter_words:
        if (cfw in title.lower()) or (cfw in ' '.join(keywords).lower()) or (cfw in description.lower()):
            return 1  # relevant

    return 0  # definitely not relevant


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

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

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
        if (covid_related != 1 and covid_related != 2) or article.meta_lang != 'tr':
            return

        if covid_related == 1:
            self.count += 1

            print(f'[RELEVANCE]:{covid_related} -- [LANG]:{article.meta_lang}')
            print(f'[TITLE]{article.title}')
            print(f'[URL]{url}')
            print(f'[COUNT]{self.count}')

            filename = ' '.join([str(elem) for elem in url.split('/')[2:]]) + '.html'
            with open("[DIRECT]" + filename, 'wb') as f:
                f.write(response.body)

            print(f'[DOWNLOADED] {filename}')

            print('#############################################')

            yield {
                'url': url,
                'title': article.title,
                'text': article.text,
                'description': article.meta_description,
                'keywords': article.meta_keywords,
                'relevance': covid_related,
                'html': filename
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

        elif covid_related == 2:

            print(f'[RELEVANCE]:{covid_related} -- [LANG]:{article.meta_lang}')
            print(f'[TITLE]{article.title}')
            print(f'[URL]{url}')
            print(f'[COUNT]{self.count} (not increased)')

            filename = ' '.join([str(elem) for elem in url.split('/')[2:]]) + '.html'
            with open("[RELATIVE]" + filename, 'w') as f:
                f.write(response.body)

            print(f'[DOWNLOADED] {filename}')

            print('#############################################')

            yield {
                'url': url,
                'title': article.title,
                'text': article.text,
                'description': article.meta_description,
                'keywords': article.meta_keywords,
                'relevance': covid_related,
                'html': filename
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
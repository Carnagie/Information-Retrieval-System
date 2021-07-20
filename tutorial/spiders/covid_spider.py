import scrapy
import time
from scrapy.linkextractors import LinkExtractor

TITLE_WORDS = ["covid19", "covid-19", "corona", "biontech", "pfizer"]
KEYWORDS = []
LANGUAGE = ["tr"]

def relevance_checker(title_text):
    flag = False
    if len(title_text) <= 0:
        return flag
    pruned_text = title_text.strip().lower()

    if any(titles in pruned_text for titles in TITLE_WORDS):
        flag = True
        print(f'[FOUND]')

    return flag


class CovidSpider(scrapy.Spider):
    name = "covids"

    def start_requests(self):
        urls = [
            'https://covid19.saglik.gov.tr/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[2]
        le = LinkExtractor()
        links = le.extract_links(response)

        print(f'[CRAWLING]: {response.url}')

        is_relevant = relevance_checker(str(response.css("title::text").get()))
        if len(response.css("title::text")) > 0:
            print(f'[TITLE] {response.css("title::text").get()}')
            print(f'[RELEVANCE] {is_relevant}')

        if is_relevant:
            filename = f'covids-{response.url}.html'

            print(f'[DOWNLOADING]: {filename}')

            with open(filename, 'wb') as f:
                f.write(response.body)
            self.log(f'Saved file {filename}')

            for link in links:
                print(f'[NEW URL] {link.url}')
                url = response.urljoin(link.url)
                time.sleep(8)
                yield scrapy.Request(url=url, callback=self.parse)

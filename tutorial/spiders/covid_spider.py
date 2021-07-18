import scrapy

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
        print(f'[CRAWLING]: {page}')

        is_relevant = relevance_checker(str(response.css("title::text").get()))
        if len(response.css("title::text")) > 0:
            print(f'[TITLE] {response.css("title::text").get()}')
            print(f'[RELEVANCE] {is_relevant}')

        if is_relevant:
            filename = f'quotes-{page}.html'

            print(f'[DOWNLOADING]: {filename}')

            with open(filename, 'wb') as f:
                f.write(response.body)
            self.log(f'Saved file {filename}')

            for href in response.css("a::attr('href')"):
                print(f'[NEW URL] {href}')
                url = response.urljoin(href.extract())
                yield scrapy.Request(url=url, callback=self.parse)

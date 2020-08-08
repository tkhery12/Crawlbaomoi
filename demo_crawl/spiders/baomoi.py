import json
import scrapy
from datetime import datetime

OUTPUT_FILENAME = 'data/data_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))


class BaomoiSpider(scrapy.Spider):
    name = 'baomoi'
    allowed_domains = ['baomoi.com']
    start_urls = [
        'https://baomoi.com'
    ]
    CRAWLED_COUNT = 0

    def parse(self, response):
        if response.status == 200:
            print('Count =', self.CRAWLED_COUNT)
            print('Crawl from :', response.url)
            data = {
                'link': response.url,
                'time': response.css('time.time::text').get(),
                'title': response.css('h1.article__header::text').get(),
                'description': response.css('div.article__sapo::text').get(),
                'content': '\n'.join([
                    ''.join(c.css('*::text').getall())
                    for c in response.css('div.article__body p.body-text')
                ]),
                'topic': '\n'.join(response.css('a.cate::text').getall()),
                'tags': [
                    k.strip() for k in response.css('div.article__tag a.keyword::text').getall()
                ],
                'sour_link': response.css('p.bm-source a::attr(href)').get()

            }
            with open(OUTPUT_FILENAME, 'a', encoding='utf8') as f:
                f.write(json.dumps(data, ensure_ascii=False))
                f.write('\n')
                print('SUCCESS:', response.url)
                self.CRAWLED_COUNT += 1
                self.crawler.stats.set_value('CRAWLED_COUNT', self.CRAWLED_COUNT)
            for data_id in response.css('div.story::attr(data-aid)').getall():
                yield response.follow('http://www.baomoi.com/a/c/' + data_id + '.epi', callback=self.parse)
            for data_id, k in response.css('a::attr(href)').getall(), response.css('a::attr(data-id)').getall():
                yield response.follow('http://www.baomoi.com/a/c' + data_id + k + '.epi', callback=self.parse)

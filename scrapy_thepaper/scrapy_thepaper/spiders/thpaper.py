import scrapy
from mongoengine import SequenceField, StringField, DateTimeField, Document
import datetime
from mongoengine import connect


HOST = 'mongo'
PORT = 27017
connect('self_spiders', host=HOST, port=PORT)


# class ThePaperSearchResults(Document):
#     id = SequenceField(primary_key=True)
#     url = StringField(required=True, unique=True)
#     title = StringField(required=True)
#     search_keyword = StringField(required=True)
#     crawl_time = DateTimeField(default=datetime.datetime.now)
#     meta = {'collection': 'thepaper_search_results'}


class ThePaperSearchResults(Document):
    id = SequenceField(primary_key=True)
    url = StringField(required=True, unique=True)
    title = StringField(required=True)
    search_keyword = StringField(required=True)
    crawl_time = DateTimeField(default=datetime.datetime.now)
    news_description = StringField(required=False)
    news_keywords = StringField(required=False)
    news_content = StringField(required=True)
    news_author = StringField(required=False)
    news_source = StringField(required=False)
    news_time = StringField(required=False)
    meta = {'collection': 'thepaper_search_results'}


results = ThePaperSearchResults.objects()


class ThePaperSpider(scrapy.Spider):
    name = 'thepaper'
    allowed_domains = ['thepaper.cn']
    # start_urls = ['https://www.thepaper.cn/newsDetail_forward_10624984']

    def start_requests(self):
        for result in results:
            yield scrapy.Request(
                url="https://www.thepaper.cn/newsDetail_forward_" + result.url,
                callback=self.parse,
                meta={'url': result.url}
            )

    def parse(self, response):
        # self.logger.info(f'Parsing detail page from {response.url}')

        # 提取元数据
        news_description = response.css('meta[name="description"]::attr(content)').get()
        news_keywords = response.css('meta[property="keywords"]::attr(content)').get()

        # 提取文章标题
        # news_title = response.css('h1.index_title__B8mhI::text').get()
        news_time = response.css('div.ant-space-item span::text').get()

        # 提取文章内容
        news_content = response.css('div.index_cententWrap__Jv8jK p::text').getall()
        news_content = ' '.join(news_content).strip()  # 将内容合并成一个字符串

        # 提取作者和来源
        news_author = response.css('div.index_left__LfzyH div::text').get()
        news_source = response.css('div.ant-space-item span::text').getall()[2]

        # self.logger.info(f'news_content: {news_content}')

        if not news_content:
            self.logger.warning(f"Failed to extract all information from {response.meta['url']}")

        # yield {
        #     'news_title':  response.meta['title'],
        #     'news_description': news_description,
        #     'news_keywords': news_keywords,
        #     'news_content': news_content,
        #     'news_author': news_author,
        #     'news_source': news_source,
        #     'news_time': news_time,
        #     'search_keyword': response.meta['search_keyword'],
        #     'url': response.meta['url']
        # }
        ThePaperSearchResults.objects(url=response.meta['url']).update_one(
            set__news_description=news_description,
            set__news_keywords=news_keywords,
            set__news_content=news_content,
            set__news_author=news_author,
            set__news_source=news_source,
            set__news_time=news_time
        )

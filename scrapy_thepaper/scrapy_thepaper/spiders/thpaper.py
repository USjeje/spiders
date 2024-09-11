import scrapy


class ThePaperSpider(scrapy.Spider):
    name = 'thepaper'
    allowed_domains = ['thepaper.cn']
    start_urls = ['https://www.thepaper.cn/newsDetail_forward_10624984']

    def parse(self, response):
        self.logger.info(f'Parsing detail page from {response.url}')

        # 提取元数据
        news_description = response.css('meta[name="description"]::attr(content)').get()
        news_keywords = response.css('meta[property="keywords"]::attr(content)').get()

        # 提取文章标题
        news_title = response.css('h1.index_title__B8mhI::text').get()
        news_time = response.css('div.ant-space-item span::text').get()

        # 提取文章内容
        news_content = response.css('div.index_cententWrap__Jv8jK p::text').getall()
        news_content = ' '.join(news_content).strip()  # 将内容合并成一个字符串

        # 提取作者和来源
        news_author = response.css('div.index_left__LfzyH div::text').get()
        news_source = response.css('div.ant-space-item span::text').getall()[2]

        yield {
            'news_title': news_title,
            'news_description': news_description,
            'news_keywords': news_keywords,
            'news_content': news_content,
            'news_author': news_author,
            'news_source': news_source,
            'news_time': news_time
        }

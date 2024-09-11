import scrapy
from scrapy_splash import SplashRequest

class SimpleSpider(scrapy.Spider):
    name = 'test_splash'

    def start_requests(self):
        yield SplashRequest(
            url='http://www.baidu.com',
            callback=self.parse_result,
            args={'wait': 0.5},
        )

    def parse_result(self, response):
        self.logger.info("************************ Response received from Splash ************************")
        self.logger.info(response.text)

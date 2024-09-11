import scrapy
from scrapy_splash import SplashRequest

class SearchSpider(scrapy.Spider):
    name = 'search'
    start_urls = ['https://www.thepaper.cn/searchResult?id=%E7%94%B5%E4%BF%A1%E8%AF%88%E9%AA%97&type=4']

    """
    splash:go(args.url): 打开指定的URL。
    splash:wait(3): 等待3秒，让页面初步加载完成。
    while not splash:select('.index_loading__6IvcD') do: 循环检查页面是否还有加载中的标志（通过选择器.index_loading__6IvcD）。
        splash:runjs("window.scrollTo(0, document.body.scrollHeight);"): 执行JavaScript代码，将页面滚动到底部，以触发更多内容的加载。
        splash:wait(3): 再次等待3秒，让新的内容加载完成。
    return {html = splash:html()}: 返回整个页面的HTML内容。
    """

    script = """
    function main(splash, args)
        splash:go(args.url)
        splash:wait(3)
        while not splash:select('.index_searchresult__KNmSI') do
            splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
            splash:wait(3)
        end
        return {html = splash:html()}
    end
    """

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': self.script})

    def parse(self, response):
        for result in response.css('div.index_searchresult__KNmSI div.mdCard'):
            link = result.css('a::attr(href)').get()
            if link:
                yield {'link': response.urljoin(link)}

import scrapy
from scrapy_splash import SplashRequest


class SearchSpider(scrapy.Spider):
    name = 'search'
    start_urls = ['https://www.thepaper.cn/searchResult?id=%E7%94%B5%E8%AF%9D%E8%AF%88%E9%AA%97&type=4']

    script = """
    function main(splash, args)
        splash:go(args.url)
        splash:wait(5)
        local scroll_count = args.scroll_count or 0
        while not splash:select('.index_loading__6IvcD') and scroll_count < 10 do
            splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
            splash:wait(5)
            scroll_count = scroll_count + 1
        end
        return {
            html = splash:html(),
            scroll_count = scroll_count
        }
    end
    """

    def start_requests(self):
        for url in self.start_urls:
            self.log(f"************* START start_requests *************")
            yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': self.script, 'scroll_count': 0})

    def parse(self, response):
        self.log(f"************* START parse *************")
        new_results = []
        for result in response.css('div.index_searchresult__KNmSI li'):
            link = result.css('div.mdCard a::attr(href)').get()
            if link:
                link = response.urljoin(link)
                text = result.css('span[style="cursor: pointer;"]::text').get()
                self.c(f"************* link = {link} *************")
                self.log(f"************* test = {text} *************")
                if text:
                    new_results.append({
                        'link': link,
                        'text': text
                    })

        # If new results are found, yield them and repeat the request with increased scroll_count
        if new_results:
            for item in new_results:
                yield item

            scroll_count = response.meta['scroll_count']
            if scroll_count < 10:
                self.log(f'Scrolling for the {scroll_count + 1} time')
                yield SplashRequest(response.url, self.parse, endpoint='execute',
                                    args={'lua_source': self.script, 'scroll_count': scroll_count + 1})
            else:
                self.log('Reached the maximum scroll count. Stopping...')
        else:
            self.log('No new results found. Stopping...')

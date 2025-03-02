import scrapy
import time
import re
from urllib.parse import quote
from scrapy.item import Item, Field
from scrapy_playwright.page import PageMethod
from ..config import condition_list


class VintedItem(Item):
    url = Field()
    title = Field()
    product_id = Field()
    search_text = Field()
    shipping_fee = Field()
    price = Field()
    is_buy = Field()
    seller_fee = Field()
    platform_fee = Field()
    met_model = Field()
    brand = Field()
    condition = Field()

class VintedSpider(scrapy.Spider):
    name = 'vinted'
    allowed_domains = ['vinted.it']
    custom_settings = {
        'CONCURRENT_REQUESTS': 32,  # 提高并发以加速详情页抓取
    }

    def start_requests(self):
        search_text = getattr(self, 'search_text', '').strip()
        if not search_text:
            self.logger.error("❌ 错误: 缺少 search_text 参数")
            raise ValueError("❌ 请使用 -a search_text=关键词 运行爬虫")

        encoded_search_text = quote(search_text)
        self.logger.info(f"🔍 搜索关键词: {search_text}")

        url = f"https://www.vinted.it/catalog?search_text={encoded_search_text}&time={int(time.time())}&order=newest_first&page=1"
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "a.new-item-box__overlay"),
                    PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight);"),
                    PageMethod("wait_for_timeout", 5000)
                ]
            }
        )

    @staticmethod
    def is_have_key(product_model, possible_names) -> bool:
        for name in possible_names:
            if name in product_model:
                return True
        return False

    def parse(self, response):
        products = response.css('a.new-item-box__overlay')
        search_text = getattr(self, 'search_text', '').strip()

        for product in products:
            # Fujifilm instax mini 70, brand: FUJIFILM, condizioni: Nuovo, €80.00, €84.70 include la Protezione acquisti
            title = product.attrib.get('title', '')
            product_model = title.split(", brand:")[0].lower()
            prices = re.findall(r'€\s*([\d,]+\.\d{2})', title)
            clean_price = lambda s: float(s.replace(',', '')) if s else None
            platform_fee = clean_price(prices[1]) if len(prices) > 1 else None
            print("++++++++++++++++++++++++++++++++++++++++++++")
            print(title)
            print(product_model, prices, platform_fee)

            is_not_need_save = True
            met_model = ''
            for condition in condition_list:
                if self.is_have_key(product_model, condition.possible_names):
                    if platform_fee and platform_fee >= condition.min_price and platform_fee <= condition.max_price:
                        is_not_need_save = False
                        met_model = condition.model
                        break
            if is_not_need_save:
                continue

            print("met yes")
            # 替换原来的 `item` 定义：
            item = VintedItem(
                url=response.urljoin(product.attrib.get('href')),
                title=product.attrib.get('title', ''),
                product_id=self.extract_product_id(product),
                search_text=search_text,
                shipping_fee=None,
                price=None,
                is_buy=False,
                seller_fee=clean_price(prices[0]) if len(prices) > 0 else None,
                platform_fee=platform_fee,
                met_model=met_model,
                brand=re.search(r'brand:\s*([^,]+)', title).group(1).strip() if 'brand:' in title else None,
                condition=re.search(r'condition:\s*([^,]+)', title).group(1).strip() if 'condition:' in title else None
            )

            # 将 item 直接返回给 Crawlab
            yield item

    def extract_product_id(self, element):
        testid = element.attrib.get('data-testid', '')
        return testid.split('--')[0].split('-')[-1] if testid else ''

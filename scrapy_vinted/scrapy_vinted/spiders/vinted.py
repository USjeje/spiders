import scrapy
import time
import re
from urllib.parse import quote
from scrapy_playwright.page import PageMethod
from ..models import VintedItem


class VintedSpider(scrapy.Spider):
    name = 'vinted'
    allowed_domains = ['vinted.co.uk']
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

        url = f"https://www.vinted.co.uk/catalog?search_text={encoded_search_text}&order=newest_first&page=1"
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

    def parse(self, response):
        products = response.css('a.new-item-box__overlay')
        search_text = getattr(self, 'search_text', '').strip()

        for product in products:
            item = {
                'url': response.urljoin(product.attrib.get('href')),
                'title': product.attrib.get('title', ''),
                'product_id': self.extract_product_id(product),
                'search_text': search_text,
                'shipping_fee': None,  # 初始化为None
                'price': None
            }
            title_data = self.parse_title(item['title'])
            item.update(title_data)

            # 第一阶段：快速保存基础数据
            self.save_to_mongo(item, is_initial=True)

            # 第二阶段：异步获取运费
            yield scrapy.Request(
                url=item['url'],
                callback=self.parse_shipping,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "h3[data-testid='item-shipping-banner-price']"),
                        PageMethod("wait_for_timeout", 2000)
                    ],
                    "item": item  # 传递item到详情页解析
                },
                priority=1  # 提高优先级以加速处理
            )

    def parse_shipping(self, response):
        item = response.meta['item']
        shipping_text = response.css(
            'h3[data-testid="item-shipping-banner-price"]::text'
        ).get()

        # 解析运费（例如："from £5.00" -> 5.00）
        self.logger.error(shipping_text)
        shipping_fee = self.extract_shipping_fee(shipping_text)
        item['shipping_fee'] = shipping_fee

        # 计算最终价格（根据业务逻辑调整）
        if item.get('platform_fee', 0):
            item['price'] = item.get('platform_fee', 0) + shipping_fee

        # 更新数据库记录
        self.save_to_mongo(item, is_initial=False)
        return item

    def extract_shipping_fee(self, text):
        if not text:
            return 0.0
        match = re.search(r'£([\d,]+\.\d{2})', text)
        return float(match.group(1).replace(',', '')) if match else 0.0

    def extract_product_id(self, element):
        testid = element.attrib.get('data-testid', '')
        return testid.split('--')[0].split('-')[-1] if testid else ''

    def parse_title(self, title):
        prices = re.findall(r'£([\d,]+\.\d{2})', title)
        clean_price = lambda s: float(s.replace(',', '')) if s else None

        return {
            'brand': re.search(r'brand:\s*([^,]+)', title).group(1).strip() if 'brand:' in title else None,
            'condition': re.search(r'condition:\s*([^,]+)', title).group(1).strip() if 'condition:' in title else None,
            'seller_price': clean_price(prices[0]) if len(prices) > 0 else None,
            'platform_fee': clean_price(prices[1]) if len(prices) > 1 else None,
        }

    def save_to_mongo(self, item, is_initial):
        update_data = {
            'set__title': item['title'],
            'set__product_id': item['product_id'],
            'set__brand': item['brand'],
            'set__condition': item['condition'],
            'set__search_text': item['search_text'],
            'set__seller_price': item['seller_price'],
            'set__platform_fee': item['platform_fee'],
        }

        if not is_initial:  # 第二阶段更新运费和价格
            update_data.update({
                'set__shipping_fee': item['shipping_fee'],
                'set__price': item['price']
            })

        try:
            VintedItem.objects(url=item['url']).update_one(
                **update_data,
                upsert=True
            )
            log_msg = "初稿保存" if is_initial else "运费更新"
            self.logger.info(f"✅ {log_msg}成功: {item['url']}")
        except Exception as e:
            self.logger.error(f"❌ 数据库操作失败: {e}")
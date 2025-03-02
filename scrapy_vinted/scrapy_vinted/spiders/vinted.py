import scrapy
import time
import re
from urllib.parse import quote
from scrapy_playwright.page import PageMethod
from ..models import VintedItem
from ..config import condition_list


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
                if product_model in condition.possible_names:
                    if platform_fee and platform_fee >= condition.min_price and platform_fee <= condition.max_price:
                        is_not_need_save = False
                        met_model = condition.model
                        break
            if is_not_need_save:
                continue

            item = {
                'url': response.urljoin(product.attrib.get('href')),
                'title': product.attrib.get('title', ''),
                'product_id': self.extract_product_id(product),
                'search_text': search_text,
                'shipping_fee': None,  # 初始化为None
                'price': None,
                'is_buy': False,
                'seller_fee': clean_price(prices[0]) if len(prices) > 0 else None,
                'platform_fee': platform_fee,
                "met_model": met_model,
                'brand': re.search(r'brand:\s*([^,]+)', title).group(1).strip() if 'brand:' in title else None,
                'condition': re.search(r'condition:\s*([^,]+)', title).group(
                    1).strip() if 'condition:' in title else None
            }

            # 第一阶段：快速保存基础数据
            self.save_to_mongo(item, is_initial=True)

    def extract_product_id(self, element):
        testid = element.attrib.get('data-testid', '')
        return testid.split('--')[0].split('-')[-1] if testid else ''

    def save_to_mongo(self, item, is_initial):
        update_data = {
            'set__title': item['title'],
            'set__product_id': item['product_id'],
            'set__brand': item['brand'],
            'set__condition': item['condition'],
            'set__search_text': item['search_text'],
            'set__seller_fee': item['seller_fee'],
            'set__platform_fee': item['platform_fee'],
            'set__met_model': item['met_model'],
            'set__is_buy': item['is_buy'],
            'set__shipping_fee': item['shipping_fee'],
            'set__price': item['price']
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
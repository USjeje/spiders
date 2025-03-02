from mongoengine import Document, StringField, DateTimeField, SequenceField, FloatField, BooleanField
import datetime
from mongoengine import connect

# 连接 MongoDB
connect("scrapy_vinted_db", host="mongodb://localhost:27017/")


class VintedItem(Document):
    id = SequenceField(primary_key=True)
    product_id = StringField(required=True, unique=True)
    url = StringField(required=True)
    title = StringField(required=True)
    brand = StringField()
    condition = StringField()
    met_model = StringField()

    seller_fee = FloatField(required=True)  # 卖家价格
    platform_fee = FloatField(required=True)  # 平台费用
    shipping_fee = FloatField()  # 邮费, shipping_fee不准，得在最后购买页才准确
    price = FloatField()  # 最终购买价格（seller_price + platform_fee）

    scraped_at = DateTimeField(default=datetime.datetime)  # 爬取时间（统一使用 UTC）
    search_text = StringField(required=True)
    is_buy = BooleanField(required=True)  # 是否已经购买

    meta = {'collection': 'vinted_items'}
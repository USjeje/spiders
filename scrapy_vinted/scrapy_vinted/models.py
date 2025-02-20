from mongoengine import Document, StringField, DateTimeField, SequenceField, FloatField, ListField
import datetime
from mongoengine import connect

# 连接 MongoDB
connect("scrapy_vinted_db", host="mongodb://localhost:27017/")


class VintedItem(Document):
    id = SequenceField(primary_key=True)
    url = StringField(required=True, unique=True)
    title = StringField(required=True)
    product_id = StringField()
    brand = StringField()
    condition = StringField()

    seller_price = FloatField()  # 卖家价格
    platform_fee = FloatField()  # 平台费用
    shipping_fee = FloatField()  # 邮费
    price = FloatField()  # 最终购买价格（seller_price + platform_fee）

    scraped_at = DateTimeField(default=datetime.datetime.utcnow)  # 爬取时间（统一使用 UTC）
    search_text = StringField()  # 关键词列表（按照空格切分）

    meta = {'collection': 'vinted_items'}
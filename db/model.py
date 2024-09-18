from mongoengine import SequenceField, StringField, DateTimeField, Document, BooleanField, ListField
import datetime

HOST = 'localhost'
PORT = 27017


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
    expect_news = BooleanField(required=False, default=False)
    generate_corpus = ListField(StringField(), required=False)
    generate_corpus_by_example = ListField(StringField(), required=False)

    meta = {'collection': 'thepaper_search_results'}

#
# if __name__ == '__main__':
#     from mongoengine import connect
#     # 连接到数据库
#     connect('self_spiders', host=HOST, port=PORT)
#     new_result = ThePaperSearchResults(id=1, url="http://example.com", source="The Paper")
#     new_result.save()

import random
import pandas as pd
from openpyxl import Workbook
from mongoengine import connect
from db import model

connect('self_spiders', host=model.HOST, port=model.PORT)

def output():
    data = []
    output_filepath = "./output/生成语料.xlsx"

    results = model.ThePaperSearchResults.objects()
    for result in results:
        search_keyword = result.search_keyword
        url = "https://www.thepaper.cn/newsDetail_forward_" + result.url
        if result.generate_corpus:
            for generate_context in result.generate_corpus:
                data.append([generate_context, None, search_keyword, url])

    # 随机打乱 data 列表的顺序
    random.shuffle(data)

    df = pd.DataFrame(data, columns=['生成文本(UserA可以不用管，后期可以换成其他代词)', '标签', '搜索关键词', '来源'])
    df.to_excel(output_filepath, index=False)


def output_2():
    data = []
    output_filepath = "./output/生成语料_by_example.xlsx"

    results = model.ThePaperSearchResults.objects()
    for result in results:
        search_keyword = result.search_keyword
        url = "https://www.thepaper.cn/newsDetail_forward_" + result.url
        if result.generate_corpus_by_example:
            for generate_context in result.generate_corpus_by_example:
                data.append([generate_context, None, search_keyword, url])

    # 随机打乱 data 列表的顺序
    random.shuffle(data)

    df = pd.DataFrame(data, columns=['生成文本(UserA可以不用管，后期可以换成其他代词)', '标签', '搜索关键词', '来源'])
    df.to_excel(output_filepath, index=False)


if __name__ == '__main__':
    # output()
    output_2()
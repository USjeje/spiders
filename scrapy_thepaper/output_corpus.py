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


def output_train_val_txt():
    train_file = './output/train.txt'
    val_file = './output/val.txt'

    input_file_path_1 = r".\output\3.山西反诈nlp模型生成训练数据标注【汇总】(2).xlsx"
    input_file_path_2 = r".\output\4.enhance.xlsx"

    df1 = pd.read_excel(input_file_path_1, engine='openpyxl', sheet_name='汇总')
    df2 = pd.read_excel(input_file_path_2, engine='openpyxl', sheet_name='Sheet1')

    label_data = {}
    all_data_len, legal_data_len = 0, 0
    for index, row in df1.iterrows():
        label = row['标签（梦兰）']
        if pd.notna(label):
            if label not in label_data:
                label_data[label] = []
            label_data[label].append(row['生成文本(UserABC可以不用管，后期可以换成其他代词)'])
            legal_data_len += 1
        all_data_len += 1

    # 代词替换
    replace_pronoun = ['他', '那个人', '那人', '刚那人', '她', '', '他们', '他们']
    for label, data in label_data.items():
        new_data = []
        for simple in data:
            new_simple = simple
            if 'userC' in simple:
                new_simple = '，'.join(simple.split('，')[1:])
                new_simple = new_simple.replace('userA', random.choice(replace_pronoun))
            elif 'userB' in simple:
                new_simple = simple.replace('userB', random.choice(replace_pronoun))
            elif 'userA' in simple:
                new_simple = simple.replace('userA', random.choice(replace_pronoun))
            elif 'UserA' in simple:
                new_simple = simple.replace('UserA', random.choice(replace_pronoun))
            # print(f"{simple} -> {new_simple}")
            new_data.append(new_simple)
        label_data[label] = new_data

    for index, row in df2.iterrows():
        label = row['标签']
        context = row['增强数据']
        if pd.notna(label) and pd.notna(context):
            label_data[label].append(context)
            legal_data_len += 1
        all_data_len += 1

    # 样本分布
    max_data_len = 0
    for label, data in label_data.items():
        if len(data) > max_data_len:
            max_data_len = len(data)
        print(f"{(label + ':'):<15} 样本数为{len(data):<10}")

    # 随机选取
    with open(train_file, 'w', encoding='utf-8') as f1, open(val_file, 'w', encoding='utf-8') as f2:
        for label, data in label_data.items():
            for context in data:
                if random.random() < 0.7:
                    f1.write(label + '\t' + context + '\n')
                else:
                    f2.write(label + '\t' + context + '\n')


if __name__ == '__main__':
    # output()
    # output_2()
    output_train_val_txt()
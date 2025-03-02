import pandas as pd


class Product:
    def __init__(self, model, possible_names, other_requirements, min_price, max_price):
        self.model = model
        self.possible_names = possible_names
        self.other_requirements = other_requirements
        self.min_price = min_price
        self.max_price = max_price


df = pd.read_csv("config.csv", header=0, encoding='utf-8')  # 读取 Excel 文件
df = df.fillna('')  # 将空值填充为空字符串，避免后续报错
condition_list = []

for index, row in df.iterrows():
    model = row['型号'].lower()
    possible_names = set(row['可能名称'].lower().split('\n'))  # 按换行符分割可能名称
    possible_names.add(model)
    other_requirements = row['其他要求'] if '其他要求' in row else None
    min_price = float(row['最低价格（不包含邮费，欧元）'])
    max_price = float(row['最高价格（不包含邮费，欧元）'])

    condition_list.append(Product(model, possible_names, other_requirements, min_price, max_price))

# 使用示例
# file_path = 'path_to_your_excel_file.xlsx'  # 替换为你的 Excel 文件路径
print("===================config===================")
for condition in condition_list:
    print(condition.__dict__)
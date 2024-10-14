"""
处理标签后的数据，替换和增强
"""
import random
import pandas as pd

from preprocessing import chatGPT
from utils.log import get_logger


# 创建一个日志记录器
# logger = get_logger('enhance_1000', 'INFO', './output')


# 读通话详情表
input_file_path = r".\output\3.山西反诈nlp模型生成训练数据标注【汇总】(2).xlsx"
output_file_path = r'.\output\enhance.xlsx'
df = pd.read_excel(input_file_path, engine='openpyxl', sheet_name='汇总')
# output_df = pd.read_excel(output_file_path, engine='openpyxl')
output_df_columns = ['增强数据', '标签', '次数', '是否验证', '验证']
output_df = pd.DataFrame(columns=output_df_columns)

# 逐行处理数据
label_data = {}
all_data_len, legal_data_len = 0, 0
for index, row in df.iterrows():
    label = row['标签（梦兰）']
    if pd.notna(label):
        if label not in label_data:
            label_data[label] = []
        label_data[label].append(row['生成文本(UserABC可以不用管，后期可以换成其他代词)'])
        legal_data_len += 1
    all_data_len += 1

# 样本分布
# logger.info(f"共有{len(label_data)}种标签，标记后样本分布：")
max_data_len = 0
for label, data in label_data.items():
    if len(data) > max_data_len:
        max_data_len = len(data)
    # logger.info(f"{(label+':'):<15} 样本数为{len(data):<10}")

# 数据增强(LLM生成，代词替换)
## 代词替换
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
        # print(f"{simple} -> {new_simple}")
        new_data.append(new_simple)
        label_data[label] = new_data

## LLM生成增强
security_prompt = f"国内外远程诈骗的手段，例如下载app、点击链接、发送短信、输入验证码、远程控制、登录支付宝或微信等涉及个人财产安全操作"
label_prompt = {
    '百万保障': f"定义：描述用户在微信或者抖音等地方有订购百万保障业务，然后以这些业务每月会扣款为理由让用户做一下高危操作（{security_prompt}）。有提到百万保障、百万保险、百万医保、百万计划类似这样的这些关键词",
    '抖音会员退费': f"定义：描述抖音会员退费退款等，如何退可以自行选择({security_prompt})。",
    '航班、机票退改签': f"定义：以航班延迟（比如起落架损坏）为理由，说给用户退款为诱饵，让用户下载app或操作支付宝等,提到航班延误+退款或者下载软件等高危操作({security_prompt})",
    '冒充保险退费': f"定义：冒充保险退费，提到保险、医保、保障等，并均结合退款或者下载软件等高危操作({security_prompt})。",
    '退款(除航班、教培)': f"定义：以各种理由(除了航班机票、教培、抖音会员和保险)说可以给用户退款,提到退款 退钱 退费这类关键词的，可以附带或不附带操作方式（{security_prompt}）",
    '教培退费': f"定义：以培训班辅导班等教辅机构的名义，说可以给用户退款,提到培训班辅导班等教辅机构+退款或者下载软件等高危操作（{security_prompt}）",
}
general_number = 5
common_prompt = (f"\n按照上述定义，输出符合定义的{general_number}句话，每句要以第一人称复述别人对自己说的话，涉及名词越真实越好，种类越多越好。"
                 f"每个句子无需序号，以句号结尾，句子间用回车连接，无需说明原因，可参考样本如下：\n")
chat_client = chatGPT.Client()

for label, data in label_data.items():
    print(f"\n开始处理label -> {label}")
    # logger.info(f"\n开始处理label -> {label}")
    # if len(data) < max_data_len:
    new_sample_data = []
    general_iter = 0
    new_data = data
    while len(new_data) < 1000:
        example_prompt = '\n'.join([random.choice(data) for _ in range(general_number)])
        prompt = label_prompt[label] + common_prompt + example_prompt
        results = chat_client.run(prompt)
        general_iter += 1

        try:
            results = results.replace('\n\n', '\n').replace(' ', '').split('\n')
        except Exception as e:
            results = results

        for result in results:
            if general_iter <= 100:
                eval_prompt = label_prompt[label] + f"\n结合上述诈骗流程定义，判断下述句子是否符合，符合返回1，不符合返回0，无需解释。\n" + result
                eval_result = chat_client.run(eval_prompt)
                try:
                    eval_result = int(eval_result)
                    if eval_result == 1:
                        new_sample_data.append([result, label, general_iter, True, eval_result])
                        new_data.append(result)
                    print(f"{eval_result} : {general_iter} -> {result}")
                    # logger.info(f"{eval_result} : {general_iter} -> {result}")
                except Exception as e:
                    print(f"eval_result = {eval_result}， 无效")
                    # logger.info(f"eval_result = {eval_result}， 无效")
                    continue
            else:
                new_sample_data.append([result, label, general_iter, False, None])
                new_data.append(result)

    new_rows_df = pd.DataFrame(new_sample_data, columns=output_df_columns)
    output_df = pd.concat([output_df, new_rows_df], ignore_index=True)

output_df.to_excel(output_file_path, index=False, engine='openpyxl')



import random
import pandas as pd
from mongoengine import connect

from db import model
from preprocessing import chatGPT


connect('self_spiders', host=model.HOST, port=model.PORT)


chat_client = chatGPT.Client()


def is_scam_news():
    """
    先根据title判断，如果是则入库，不是则继续根据新闻内容判断
    :return:
    """

    results = model.ThePaperSearchResults.objects()
    for result in results:
        if result.id < 1363:
            continue
        prompt_1 = (f"请你根据这个新闻标题判断，该新闻是否报道诈骗相关信息，"
                    f"若是，则返回整数0，若不是返回整数1，若不确定需要更多信息，则返回整数2"
                    f"请注意，你的回答只能从整数0,1,2中选择！\n"
                    f"新闻标题为:\n{result.title}\n"
                    f"请注意，你的回答只能从整数0,1,2中选择！")
        output = int(chat_client.run(prompt_1))
        print(f"url = {result.url}, title = {result.title}, output = {output}")
        if output == 0:
            model.ThePaperSearchResults.objects(url=result.url).update_one(set__expect_news=True)
        elif output == 1:
            model.ThePaperSearchResults.objects(url=result.url).update_one(set__expect_news=False)
        elif output == 2:
            prompt_2 = (f"我将提供一篇新闻，请你帮我判断该新闻是否报道诈骗相关的案例，"
                        f"若是，则返回整数0，若不是返回整数1"
                        f"请注意，你的回答只能从整数0,1中选择！\n"
                        f"新闻内容为:\n{result.news_content}\n"
                        f"请注意，你的回答只能从整数0,1中选择！")
            output = int(chat_client.run(prompt_2))
            print(f"url = {result.url}, title = {result.title}, output = {output}")
            if output == 0:
                model.ThePaperSearchResults.objects(url=result.url).update_one(set__expect_news=True)
            elif output == 1:
                model.ThePaperSearchResults.objects(url=result.url).update_one(set__expect_news=False)


def random_int(end, start=0):
    return random.randint(start, end)


def get_zhapian_corpus(filepath, sheet_name):
    df = pd.read_excel(filepath, sheet_name=sheet_name)

    corpus = []
    for dialogue in df['客户对话内容']:
        corpus.append(dialogue)
    return corpus



def colloquialism():
    results = model.ThePaperSearchResults.objects()
    is_colloquialism_news_title = set()
    is_colloquialism_news_description = set()

    continue_id = 0
    for result in results:
        if result.id < continue_id:
            continue
        if result.title in is_colloquialism_news_title or result.news_description in is_colloquialism_news_description:
            continue
        if not result.expect_news:
            continue

        prompt_1 = (f"我将提供一篇新闻，请你帮我判断该新闻是否报道诈骗相关的案例，"
                    f"若是，则返回整数0，若不是返回整数1"
                    f"请注意，你的回答只能从整数0,1中选择！\n"
                    f"新闻内容为:\n{result.news_content}\n"
                    f"请注意，你的回答只能从整数0,1中选择！")
        output = int(chat_client.run(prompt_1))
        print(f"id = {result.id}, url = {result.url}, title = {result.title}, output = {output}")
        if output == 0:
            prompt_2 = (f"现在有一个场景，共有三个人，分别为userA，userB，userC。"
                        f"userA看到了一篇介绍诈骗案例的新闻，于是他想模仿其中的套路进行诈骗,"
                        f"于是userA打电话给userB，打算对UserB进行诈骗。"
                        f"但userB并不知晓是否为诈骗。"
                        f"之后，当userA与userB通话完成后，userC打电话询问userB，"
                        f"userC询问userB，我们是反诈中心的，当时通话内容能和我们简单描述一下吗？"
                        f"userB该如何给userB说呢？\n"
                        f"userA看到的新闻内容如下：\n{result.news_content}\n"
                        f"userB会如何给userC描述他与userA的通话呢？请用两三句话描述，且符合通话场景。你可以产生10句话。"
                        f"输出的格式严格按照下述约定，例如：\n"
                        f"1. xxx\n"
                        f"2. xxx\n"
                        f"3. xxx\n"
                        f"4. xxx\n"
                        f"5. xxx\n"
                        f"6. xxx\n"
                        f"7. xxx\n"
                        f"8. xxx\n"
                        f"9. xxx\n"
                        f"10. xxx\n"
                        )
            output = chat_client.run(prompt_2)
            is_colloquialism_news_title.add(result.title)
            is_colloquialism_news_description.add(result.news_description)
            generate_corpus = []
            try:
                generate_corpus = [generate_corpus.split('. ')[1] for generate_corpus in output.split("\n")]
                is_retry_continue = False
            except Exception as e:
                print(f"Retry")
                is_retry_continue = True

            if is_retry_continue:
                output = chat_client.run(prompt_2)
                try:
                    generate_corpus = [generate_corpus.split('. ')[1] for generate_corpus in output.split("\n")]
                except Exception as e:
                    print(f"Retry fail")
                    continue
            else:
                print(generate_corpus)
                generate_corpus.extend(result.generate_corpus)
            model.ThePaperSearchResults.objects(url=result.url).update_one(set__generate_corpus=generate_corpus)

        elif output == 1:
            model.ThePaperSearchResults.objects(url=result.url).update_one(set__expect_news=False)


def colloquialism_by_example():
    results = model.ThePaperSearchResults.objects()
    is_colloquialism_news_title = set()
    is_colloquialism_news_description = set()

    zhapian_corpus = get_zhapian_corpus(
        filepath=r"C:\Users\Administrator\Documents\Tencent Files\2533977198\FileRecv\山西反诈语料.xlsx",
        sheet_name="整理后语料"
    )
    len_zhapian_corpus = len(zhapian_corpus) - 1

    continue_id = 298
    for result in results:
        if result.id < continue_id:
            continue
        if result.title in is_colloquialism_news_title or result.news_description in is_colloquialism_news_description:
            continue
        if len(result.generate_corpus) == 0:
            continue
        if not result.expect_news:
            continue
        if len(result.generate_corpus_by_example) != 0:
            continue

        prompt = (
            f"现在有一个场景，共有三个人，分别为userA，userB，userC。"
            f"userA看到了一篇介绍诈骗案例的新闻，于是他想模仿其中的套路进行诈骗,"
            f"于是userA打电话给userB，打算对UserB进行诈骗。"
            f"但userB并不知晓是否为诈骗。"
            f"之后，当userA与userB通话完成后，userC打电话询问userB，"
            f"userC询问userB，我们是反诈中心的，当时通话内容能和我们简单描述一下吗？"
            f"userB该如何给userB说呢？\n"
            f"userA看到的新闻内容如下：\n{result.news_content}\n"
            f"请结合所给的新闻，推测userB会如何给userC描述他与userA的通话呢？请用两三句话描述，且符合通话场景。你可以产生10句话。"
            f"输出的格式严格按照下述约定，例如userB说话的语气可能如下，但需结合场景给出10句话：\n"
            f"1. {zhapian_corpus[random_int(len_zhapian_corpus)]}\n"
            f"2. {zhapian_corpus[random_int(len_zhapian_corpus)]}\n"
            f"3. {zhapian_corpus[random_int(len_zhapian_corpus)]}\n"
            f"4. {zhapian_corpus[random_int(len_zhapian_corpus)]}\n"
            f"5. {zhapian_corpus[random_int(len_zhapian_corpus)]}\n"
            f"6. {zhapian_corpus[random_int(len_zhapian_corpus)]}\n"
            f"7. {zhapian_corpus[random_int(len_zhapian_corpus)]}\n"
            f"8. {zhapian_corpus[random_int(len_zhapian_corpus)]}\n"
            f"9. {zhapian_corpus[random_int(len_zhapian_corpus)]}\n"
            f"10. {zhapian_corpus[random_int(len_zhapian_corpus)]}\n"
        )
        output = chat_client.run(prompt)
        is_colloquialism_news_title.add(result.title)
        is_colloquialism_news_description.add(result.news_description)
        generate_corpus_by_example = []
        try:
            generate_corpus_by_example = [generate_corpus.split('. ')[1] for generate_corpus in output.split("\n")]
            is_retry_continue = False
        except Exception as e:
            print(f"id = {result.id}, Retry")
            is_retry_continue = True

        if is_retry_continue:
            output = chat_client.run(prompt)
            try:
                generate_corpus_by_example = [generate_corpus.split('. ')[1] for generate_corpus in output.split("\n")]
            except Exception as e:
                print(f"id = {result.id}, Retry fail")
                continue

        print(f"id = {result.id}, {generate_corpus_by_example}")
        generate_corpus_by_example.extend(result.generate_corpus_by_example)
        model.ThePaperSearchResults.objects(url=result.url).update_one(set__generate_corpus_by_example=generate_corpus_by_example)


if __name__ == '__main__':
    # is_scam_news()
    # colloquialism()
    colloquialism_by_example()
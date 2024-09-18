import time
# import docx
# import xlwt
# from docx.oxml.ns import qn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from mongoengine import connect
from db import model

connect('self_spiders', host=model.HOST, port=model.PORT)
SEARCH_KEYWORDS = ['微信百万保障', '机票退改签', '冒充抖音客服', '退费诈骗', '退款诈骗']


def main():
    search_word = SEARCH_KEYWORDS
    search_word_len = search_word.__len__()
    dict = {}  # 记录是否重复的字典
    num = -1    # 记录标题数
    search_word_num = 0   # 搜索到第几个词
    name_text = []
    name_href = []
    driver = webdriver.Edge()
    driver.get("https://www.thepaper.cn/")
    time.sleep(1)
    for word in search_word:
        search_word_num = search_word_num + 1
        search = driver.find_element(By.TAG_NAME, 'input')
        search.send_keys(word)
        time.sleep(1)

        # x_path = "//main/div/div/div/div/div/div/div/span"
        # x_path = "//main/div[1]/div/div/div/div/div[3]/div[1]"
        # 定位搜索框，输入搜索关键词，并模拟点击
        search_x_path = "//main/div[1]/div/div/div/div/div[3]/div[1]/span"
        send_button = driver.find_element(By.XPATH, search_x_path)
        ActionChains(driver).move_to_element(send_button).click(send_button).perform()
        time.sleep(2)

        x_path = "//main/div[3]/div[1]/div/div[2]/div/ul/li[5]"
        send_button = driver.find_element(By.XPATH, x_path)
        ActionChains(driver).move_to_element(send_button).click(send_button).perform()
        time.sleep(2)

        # 获取当前页面的高度
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        last_height = driver.execute_script("return document.body.scrollHeight")

        # 选取页面后，往下滑
        count = 0
        while True:  # 模拟下拉操作，直到滑动到底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 模拟下拉操作
            time.sleep(1.5)  # 等待页面加载
            new_height = driver.execute_script("return document.body.scrollHeight")  # 获取当前页面的高度
            count += 1
            if new_height == last_height or count >= 20:  # 判断是否已经到达页面底部
                break
            last_height = new_height

        x_path = "//main/div[3]/div[1]/div/div/div/ul/li/div/a"
        names = driver.find_elements(By.XPATH, x_path)
        for name in names:
            # if name.text not in dict:
            name_text.append(name.text)
            name_href.append(name.get_attribute("href"))
            num = num+1
            # dict[name.text] = 1
            title = name.text
            url = name.get_attribute("href")
            url_unique_id = url.split('_')[-1]
            print(url_unique_id)
            try:
                model.ThePaperSearchResults(
                    url=url_unique_id,
                    title=title,
                    search_keyword=word,
                ).save()
            except Exception as e:
                continue

        driver.get("https://www.thepaper.cn/")
        time.sleep(5)

    #     if search_word_num == search_word_len:
    #
    #         file = docx.Document()    #创建docx对象
    #
    #         workbook = xlwt.Workbook()
    #         sheet1 = workbook.add_sheet('sheet1', cell_overwrite_ok=True)
    #         sheet1.write(0, 0, '标题')
    #         sheet1.write(0, 1, '链接')
    #         for i in range(num+1):
    #             print(name_text[i])
    #             print(name_href[i])
    #             try:
    #                 address = name_href[i]
    #                 driver.get(address)
    #             except:
    #                 print("网址失效")
    #             file.add_paragraph(name_text[i])
    #             sheet1.write(i+1, 0, name_text[i])
    #             sheet1.write(i + 1, 1, name_href[i])
    #             try:
    #                 x_path = "//main/div[4]/div[1]/div[1]/div/h1"
    #                 title = driver.find_element(By.XPATH, x_path)
    #                 x_path = "//main/div[4]/div[1]/div[1]/div/div[2]"
    #                 article = driver.find_element(By.XPATH, x_path)
    #                 print(title.text)
    #                 print(article.text)
    #                 file.add_paragraph(article.text)
    #             except:
    #                 print("非文字")
    #         for para in file.paragraphs:
    #             for run in para.runs:
    #                 run.font.size = docx.shared.Pt(10)  # 设置字体大小为10
    #                 run.font.name = 'Times New Roman' # 英文
    #                 run._element.rPr.rFonts.set(qn('w:eastAsia'), u'楷体')  # 中文
    #         file.save("crawlerResult.docx")
    #
    #         workbook.save('./crawlerResult.xls')
    #     else:
    #         driver.close()
    # print(dict.keys())


if __name__ == '__main__':
    main()

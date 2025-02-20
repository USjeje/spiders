import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# 设置 Chrome 浏览器参数
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--user-data-dir=C:\\Users\\你的用户名\\AppData\\Local\\Google\\Chrome\\User Data")  # 让脚本使用你当前的登录状态
options.add_argument("--profile-directory=Default")  # 使用默认 Chrome 账号

driver = webdriver.Chrome(options=options)  # 启动浏览器
driver.get("https://www.vinted.com/")  # 访问 Vinted 网站

# 搜索商品
def search_product():
    search_box = driver.find_element(By.NAME, "search_text")
    search_box.clear()  # 清空搜索框
    search_box.send_keys("Fujifilm Instax")  # 搜索所有 Fujifilm Instax 相关商品
    search_box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(3, 6))  # 模拟人类浏览，间隔 3 到 6 秒

# 检查商品是否符合购买条件
def check_product():
    items = driver.find_elements(By.CSS_SELECTOR, ".item-box")
    for item in items:
        try:
            price = float(item.find_element(By.CSS_SELECTOR, ".price").text.strip("€").replace(",", "."))
            title = item.find_element(By.CSS_SELECTOR, ".title").text

            # 判断是否符合购买条件
            if "Wide 300" in title and price < 180:
                buy_item(item)
            elif "SQ6" in title and price < 110:
                buy_item(item)
            elif "Mini 90" in title and "brown" in title.lower() and price < 150:
                buy_item(item)
            elif "Mini 90" in title and "black" in title.lower() and price < 100:
                buy_item(item)

        except Exception as e:
            print(f"Error checking item: {e}")

# 购买商品
def buy_item(item):
    item.click()  # 点击商品
    time.sleep(random.uniform(2, 4))  # 模拟用户浏览商品页面

    try:
        # 如果有"添加到购物车"按钮，点击它
        add_to_cart_button = driver.find_element(By.CSS_SELECTOR, ".add-to-cart-button")
        add_to_cart_button.click()
        time.sleep(random.uniform(2, 3))  # 等待商品添加完成

        # 进入购物车结账
        driver.get("https://www.vinted.com/cart")
        time.sleep(random.uniform(2, 3))

        # 自动选择送货方式
        select_shipping()

        # 确认订单并支付
        confirm_button = driver.find_element(By.CSS_SELECTOR, ".confirm-order-button")
        confirm_button.click()
        time.sleep(random.uniform(2, 3))  # 模拟支付过程

        print("购买成功！")
    except Exception as e:
        print(f"Error during purchase: {e}")

# 选择送货方式
def select_shipping():
    try:
        # 优先选择"送货上门"选项
        home_delivery_button = driver.find_element(By.CSS_SELECTOR, ".home-delivery-option")
        home_delivery_button.click()
        print("已选择送货上门")
    except:
        try:
            # 如果没有送货上门，则选择最近的代收点
            collect_point_button = driver.find_element(By.CSS_SELECTOR, ".delivery-point-selection")
            collect_point_button.click()
            print("已选择最近的代收点")
        except:
            print("未找到送货选项，可能无法购买")

# 运行脚本
def run():
    while True:
        search_product()
        check_product()
        # 每次搜索后等待 10 到 20 秒，模拟人类操作
        time.sleep(random.uniform(10, 20))

# 开始运行
run()



# python使用scrapy_playwright再centos上模拟网站的账号登录和账号设置，浏览器的步骤如下：
# 1.点击动态加载网址：https://www.vinted.co.uk/的该按钮：
# <a role="button" href="/member/signup/select_type?ref_url=%2F" class="web_ui__Button__button web_ui__Button__outlined web_ui__Button__small web_ui__Button__primary web_ui__Button__truncated" data-testid="header--login-button"><span class="web_ui__Button__content"><span class="web_ui__Button__label">Sign up | Log in</span></span></a>
# 2.出现一个小窗口，点击log in：
# <span class="web_ui__Text__text web_ui__Text__body web_ui__Text__left web_ui__Text__primary web_ui__Text__underline">Log in</span>
# 3.窗口内容变化，点击emial：
# <span class="web_ui__Text__text web_ui__Text__body web_ui__Text__left web_ui__Text__primary web_ui__Text__underline">email</span>
# 4.出现登录窗口，如图所示，账号和密码元素分别为：
# <input class="web_ui__Input__value" id="username" placeholder="Email or username" type="text" name="username">
# <input class="web_ui__Input__value web_ui__Input__with-suffix" id="password" placeholder="Password" type="password" name="password">
# 5.模拟输入账号密码后，点击con按钮，元素为：
# <button type="submit" class="web_ui__Button__button web_ui__Button__filled web_ui__Button__default web_ui__Button__primary web_ui__Button__truncated"><span class="web_ui__Button__content"><span class="web_ui__Button__label">Continue</span></span></button>
#
# 无法自动登录，有人机验证，服务器最好为windows
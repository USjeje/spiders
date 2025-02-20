from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 连接到已打开的 Edge
edge_options = Options()
edge_options.debugger_address = "127.0.0.1:9222"  # 连接到调试端口

# 连接到已打开的 Edge（不会新开窗口）
driver = webdriver.Edge(options=edge_options)

# **等待 Edge 连接成功**
time.sleep(2)  # 等待 2 秒，确保连接成功

# **检查是否连接到 Edge**
print("当前打开的标签页：", driver.window_handles)

# **新建标签页**
driver.execute_script("window.open('about:blank', '_blank');")  # 打开空白页
driver.switch_to.window(driver.window_handles[-1])
print("切换到新标签页")

# **访问目标网站**
url = "https://www.vinted.co.uk/items/5776646043-fujifilm-instax-link-mini-2?referrer=catalog"
driver.get(url)
print(f"打开网站: {url}")

# **等待 "Buy now" 按钮出现并点击**
try:
    buy_now_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='item-buy-button']"))
    )
    buy_now_button.click()
    print("成功点击 'Buy now' 按钮")

    # **等待页面跳转**
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

    # **等待 "Pay" 按钮出现并点击**
    pay_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='purchase']"))
    )
    pay_button.click()
    print("成功点击 'Pay' 按钮！")

except Exception as e:
    print(f"出现错误: {e}")

finally:
    # **只关闭新标签页，不关闭整个浏览器**
    driver.close()
    print("关闭新标签页")

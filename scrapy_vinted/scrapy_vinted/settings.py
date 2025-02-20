BOT_NAME = "scrapy_vinted"

SPIDER_MODULES = ["scrapy_vinted.spiders"]
NEWSPIDER_MODULE = "scrapy_vinted.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# 下载延迟，遵守爬虫礼仪
DOWNLOAD_DELAY = 1

# 启用 Playwright 用于动态内容渲染
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_BROWSER_TYPE = "chromium"  # 使用 Chromium 浏览器
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}  # 无头模式，后台运行

# 禁用 Splash 相关的中间件（避免冲突）
DOWNLOADER_MIDDLEWARES = {}

# 禁用不必要的管道
ITEM_PIPELINES = {}

MONGODB_URI = "mongodb://localhost:27017/"
MONGODB_DB = "scrapy_db"

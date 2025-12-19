BOT_NAME = "email_crawler"
SPIDER_MODULES = ["email_crawler.spiders"]
NEWSPIDER_MODULE = "email_crawler.spiders"

# (de scrapy-playwright, mantén esto)
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 15000

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

ROBOTSTXT_OBEY = False

LOG_LEVEL = "INFO"

custom_settings = {
    "OFFSITE_ENABLED": False,
}


# Paraleo de requests
CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 16
DOWNLOAD_DELAY = 0  # o 0.25 si el sitio es sensible

# Si usás Playwright, limita el “peso” del browser
PLAYWRIGHT_MAX_CONTEXTS = 2
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4
# (subí/bajá estos dos con cuidado; cada página es un ‘tab’ real)

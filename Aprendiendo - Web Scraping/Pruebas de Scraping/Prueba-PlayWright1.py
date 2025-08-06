from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://www.venex.com.ar/notebooks/notebook-lenovo-ideapad-slim-3-15amn8-ryzen-5-7520u-8gb-ssd-512gb-15-6-free-arctic-grey.html")

    print(page.query_selector_all("meta")[10].get_attribute("content"))
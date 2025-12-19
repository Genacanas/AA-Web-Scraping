from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    url = "https://www.upwork.com/nx/search/jobs/?nbs=1&q=web%20scraping&page=1&per_page=50"
    page.goto(url)
    # page.screenshot(path="captcha.png")
    print("Captcha screenshot saved as captcha.png")
    page.wait_for_selector("h5 mb-0 mr-2 job-tile-title")
    page.wait_for_timeout(10000)  # Espera 10 segundos para que el usuario resuelva el captcha manualmente
    browser.close()

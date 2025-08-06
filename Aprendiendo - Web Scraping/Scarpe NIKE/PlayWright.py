from playwright.sync_api import sync_playwright
import pandas as pd

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) #CAMBIAR A TRUE SI NO QUEREMOS VER EL NAVEGADOR
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    page = context.new_page()

    url = "https://www.nike.ae/en/home/"
    page.goto(url)
    #la pagina cambia cuando la inspecciono
    page.wait_for_selector("button.b-header__toggle-nav.js-menu-open")
    menu = page.locator("button.b-header__toggle-nav.js-menu-open")
    menu.hover()
    page.wait_for_selector("span.b-megamenu__link-text.js-megamenu__link-text")
    page.locator("span.b-megamenu__arrowtoggle icon icon-nav-caret-right icon--flip").click()
    page.query_selector_all("span.b-megamenu__arrowtoggle.icon.icon-nav-caret-right.icon--flip")[1].click()
    
    page.query_selector_all("span.b-megasubmenu__link-text.js-megamenu__link-text")[1].click()
    page.wait_for_timeout(2000)

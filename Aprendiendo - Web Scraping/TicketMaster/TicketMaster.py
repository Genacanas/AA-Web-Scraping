from playwright.sync_api import sync_playwright
import time
import json
from random import randint


def scrape_ticket():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) #CAMBIAR A TRUE SI NO QUEREMOS VER EL NAVEGADOR
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")

        #Cargar Cookies
        with open("C:/Users/genar/OneDrive/Documentos/Aprendiendo - Web Scraping/TicketMaster/cookies.json", "r") as f:
            cookies = json.load(f)
            context.add_cookies(cookies)

        page = context.new_page()
        url = "https://www.booking.com/?aid=348858&label=pc-ar-booking-booking-sd-tsex"
        page.goto(url)

        page.wait_for_selector("input.c-autocomplete__input.sb-searchbox__input.sb-destination__input")
        page.wait_for_timeout(5838)

        page.locator("input.c-autocomplete__input.sb-searchbox__input.sb-destination__input").click()

        text = "miami"
        for char in text:
            page.keyboard.type(char)
            time.sleep(0.15)

        page.wait_for_timeout(15209)

        page.locator("span.sb-date-field__icon.sb-date-field__icon-btn.bk-svg-wrapper.calendar-restructure-sb").click()
        #page.wait_for_timeout(1029)
        #page.query_selector_all("td.bui-calendar__date")[29].click()
        #page.wait_for_timeout(1748)
        #page.query_selector_all("td.bui-calendar__date")[55].click()
        #page.wait_for_timeout(2432)
        #page.locator("div.sb-searchbox-submit-col.-submit-button ").click()
        
        #page.wait_for_selector("span.ef785aa7f4")
        #page.wait_for_timeout(1022)
        #page.locator("span.ef785aa7f4").click()
        browser.close()

scrape_ticket()
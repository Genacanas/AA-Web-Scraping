from playwright.sync_api import sync_playwright
import json

def save_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) #CAMBIAR A TRUE SI NO QUEREMOS VER EL NAVEGADOR
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0")

        page = context.new_page()
        url = "https://www.booking.com/?aid=348858&label=pc-ar-booking-booking-sd-tsex"
        page.goto(url)
        page.wait_for_timeout(5000)
        page.wait_for_selector("span.sb-date-field__icon.sb-date-field__icon-btn.bk-svg-wrapper.calendar-restructure-sb")
        # Guarda las cookies
        cookies = context.cookies()
        with open("cookies.json", "w") as f:  # Cambia a modo "w" para escribir el archivo
            json.dump(cookies, f)

        print("Cookies guardadas exitosamente.")
        browser.close()


save_cookies()
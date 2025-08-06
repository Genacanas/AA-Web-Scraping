from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import pandas as pd
import os

ua = UserAgent()
filename = "array_data.xlsx"
filename2 = "data_buffer.xlsx"
data = []
data_buffer = []

def scroll_gradualmente_hasta_pixels(page, target_pixels, step=500, delay=0.5, max_intentos=50):
    intentos = 0
    while intentos < max_intentos:
        current_scroll = page.evaluate("() => window.pageYOffset")
        print(f"Posición actual: {current_scroll} pixeles")

        if current_scroll >= target_pixels:
            print(f"✅ Se alcanzó el objetivo de {target_pixels} pixeles.")
            return

        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(delay)

        new_scroll = page.evaluate("() => window.pageYOffset")
        if new_scroll == current_scroll:
            intentos += 1
            print(f"Sin cambio en el scroll. Intento {intentos}/{max_intentos}.")
        else:
            intentos = 0

    print(f"⚠️ Se agotaron los intentos sin alcanzar {target_pixels} pixeles.")

def scroll_gradualmente_hasta_el_final(page, step=500, delay=0.5, max_intentos=50):
    intentos = 0
    last_scroll_height = 0

    while intentos < max_intentos:
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(delay)

        current_scroll_height = page.evaluate("document.body.scrollHeight")

        if current_scroll_height == last_scroll_height:
            intentos += 1
        else:
            intentos = 0

        last_scroll_height = current_scroll_height

    print("✅ Scroll completo. Se alcanzó el final o no hay más contenido.")

def scroll_y_click_load_more(page, step=500, delay=1, max_intentos=50):
    intentos = 0
    last_scroll_height = page.evaluate("document.body.scrollHeight")

    while intentos < max_intentos:
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(delay)

        try:
            button = page.query_selector("div.load-more-container")
            if button:
                button.click()
                time.sleep(delay)
                print("🟢 Botón clickeado.")
        except Exception as e:
            print(f"⚠️  Error al intentar clickear el botón: {e}")

        current_scroll_height = page.evaluate("document.body.scrollHeight")
        if current_scroll_height == last_scroll_height:
            intentos += 1
        else:
            intentos = 0
        last_scroll_height = current_scroll_height

    print("✅ Scroll completo. Se alcanzó el final o no hay más contenido.")

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
        page = context.new_page()

        page.goto("https://www.shiksha.com/engineering/ranking/top-engineering-colleges-in-india/44-2-0-0-0")
        page.wait_for_timeout(1000)

        scroll_y_click_load_more(page)

        page.wait_for_timeout(3000)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        name_universities = soup.find_all("h4", class_="f14_bold link")
        name_U = [name.text for name in name_universities]

        print(f"Nombres extraidos {name_U}")

        titles = soup.find_all("a", class_="rank_clg ripple dark")
        universities = [title.attrs.get("href") for title in titles]
        print(f"Universidades extraidas {universities}")

        name_U = name_U[95:]  # si querés omitir los primeros
        universities = universities[95:]
        numeroNombres = len(name_U)
        print(f"Name U {name_U}")
        print(f"Numero de universidades extraidas {numeroNombres}")

scrape()
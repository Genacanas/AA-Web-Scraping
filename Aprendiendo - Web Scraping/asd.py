from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent
import time
import random

ua = UserAgent().random
print(ua)

def abrir_navegador():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Asegúrate de que headless=False
        page = browser.new_page()
        page.goto("https://www.venex.com.ar/pagina-inicial.htm")
        # for i in range(0, 1000, 100):
        #     page.mouse.wheel(0, i)
        #     time.sleep(random.uniform(0.1, 0.3))

        print("Navegador abierto exitosamente")
        browser.close()

abrir_navegador()

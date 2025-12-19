from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys

sys.stdout.reconfigure(encoding="utf-8")

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"


def scroll_gradualmente_hasta_el_final(page, step=500, delay=0.5, max_intentos=5):
    intentos = 0
    last_scroll_height = 0

    while intentos < max_intentos:
        # Baja un poco
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(delay)

        # Esperar un poquito a que cargue
        current_scroll_height = page.evaluate("document.body.scrollHeight")

        if current_scroll_height == last_scroll_height:
            intentos += 1  # no creció, vamos contando intentos vacíos
        else:
            intentos = 0  # se cargó algo nuevo, reiniciamos el contador

        last_scroll_height = current_scroll_height

    print("✅ Scroll completo. Se alcanzó el final o no hay más contenido.")

data = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    context = browser.new_context(ignore_https_errors=True, user_agent=user_agent)
    page = context.new_page()
    url = "https://albertasoccer.com/member-districts"
    page.goto(url)
    scroll_gradualmente_hasta_el_final(page, step=1100, delay=0.5)

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    full_boxes = soup.select("div.elementor-element.elementor-element-adbb713.e-con-full.rounded.e-flex.e-con.e-child.animated.fadeInRight")
    print(len(full_boxes))

    for box in full_boxes:

        facebook = ""
        instagram = ""
        twitter = ""
        email = ""
        website = ""
        
        name = box.select_one("h6.elementor-heading-title.elementor-size-default").text.strip()
        print(name)
        items = box.select("a.elementor-icon")

        for item in items:
            href = item.get("href")
            if "facebook" in href:
                facebook = href
            elif "instagram" in href:
                instagram = href
            elif "twitter" in href:
                twitter = href
            elif "mailto:" in href:
                email = href.replace("mailto:", "")

        # print(facebook, instagram, twitter, email)
        try:
            website = box.select_one("a.elementor-button.elementor-button-link.elementor-size-sm").get("href")  
        except:
            website = ""
        data.append({
            "ClubName": name,
            "Phone": "",
            "Email": email,
            "Website": website,
            "instagram": instagram,
            "facebook": facebook,
            "twitter": twitter
        })
        print(data)


pd.DataFrame(data).to_excel("FutbolClubs.xlsx", index=False)    

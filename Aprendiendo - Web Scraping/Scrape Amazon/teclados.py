from playwright.sync_api import sync_playwright
import pandas as pd
from fake_useragent import UserAgent

ua = UserAgent()

# proxies = [
#     "http://proxy1:port1",
#     "http://proxy2:port2",
#     "http://proxy3:port3",
#     # Agrega más proxies aquí
# ]


data = []
def scrape_notebooks():
    #INICIAR PLAYWRIGHT
    with sync_playwright() as p:
        headers = ua.random

        browser = p.chromium.launch(headless=False) #CAMBIAR A TRUE SI NO QUEREMOS VER EL NAVEGADOR
        context = browser.new_context(user_agent=headers)
        page = context.new_page()
        #ABRE LA PAG WEB
        url = "https://www.amazon.com/s?k=teclado+inalambricos&__mk_es_US=ÅMÅŽÕÑ&crid=1JZX1JNTEMZOU&sprefix=teclado+inalambricos%2Caps%2C328&ref=nb_sb_noss_2"
        page.goto(url)

        page.wait_for_selector("a.a-link-normal.s-no-outline")
        page.wait_for_timeout(1500)
        #ENCUENTRA EL BOTON CON EL LINKS DE LAS NOTEBOOKS Y LO CLIQUEA
        items = page.locator("a.a-link-normal.s-no-outline")
        a = items.count()
        teclados = []
        for i in range(a):
            #HAGA CLICK EN EL PRIMER PRODUCTO
            items.nth(i).click()

            page.wait_for_selector("span.a-size-large.product-title-word-break")
            page.wait_for_timeout(1000)
            #EXTRAER NOMBRE, PRECIO Y CUOTAS DE LA PAG
            nombre = page.locator("span.a-size-large.product-title-word-break").inner_text()
            precio = page.locator("span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay").inner_text()
            carac = page.locator("div.form-control.ui-autocomplete-input").inner_text()

            #ALMACENO LOS DATOS EN UN ARREGLO
            teclados.append({"Nombre": nombre, "Precio": precio, "Caracteristicas": carac,"N": i+1})
            entry = {
                "Name": nombre,
                "Price": precio,
                "Characteristics ": carac
            }
            data.append(entry)
            #REGRESO A LA PAG ANTERIOR 
            page.go_back()

            #ESPERO A QUE CARGUEN DE NUEVO LOS PRODUCTOS
            page.wait_for_selector("a.a-link-normal.s-no-outline")

        browser.close()    
        return teclados

# for proxy in proxies:
#     try:
#         scrape_notebooks(proxy)
#     except Exception as e:
#         print(f"Error with proxy {proxy}: {e}")
scrape_notebooks()

df = pd.DataFrame(data)
df.to_excel("teclados.xlsx", index=False, engine='openpyxl')
from playwright.sync_api import sync_playwright
import pandas as pd

data = []
def scrape_notebooks():
    #INICIAR PLAYWRIGHT
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) #CAMBIAR A TRUE SI NO QUEREMOS VER EL NAVEGADOR
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0")
        page = context.new_page()
        #ABRE LA PAG WEB
        url = "https://www.venex.com.ar/pagina-inicial.htm"
        page.goto(url)

        page.wait_for_selector("h4.section-title.hidden-xs.mt1")
        #ENCUENTRA EL BOTON CON EL LINKS DE LAS NOTEBOOKS Y LO CLIQUEA
        page.locator("h4.section-title.hidden-xs.mt1").locator("a").click()
        page.wait_for_selector("div.product-box")

        items = page.locator("div.product-box")
        #print(items)
        #total_items = items.count()

        notebooks = []
        
        # page.wait_for_selector("div.product-box")
        
        for i in range(items.count()):
            #HAGA CLICK EN EL PRIMER PRODUCTO
            items.nth(i).click()

            page.wait_for_selector("h1.tituloProducto.hidden-xs")
            #EXTRAER NOMBRE, PRECIO Y CUOTAS DE LA PAG
            nombre = page.locator("h1.tituloProducto.hidden-xs ").inner_text()
            precio = page.locator("div.textPrecio.text-green").inner_text()
            cuotas = page.locator("div.form-control.ui-autocomplete-input").inner_text()

            #ALMACENO LOS DATOS EN UN ARREGLO
            notebooks.append({"Nombre": nombre, "Precio": precio, "Cuotas": cuotas, "N": i+1})
            entry = {
                "Name": nombre,
                "Price": precio,
                "Quotas": cuotas
            }
            data.append(entry)
            #REGRESO A LA PAG ANTERIOR 
            page.go_back()

            #ESPERO A QUE CARGUEN DE NUEVO LOS PRODUCTOS
            page.wait_for_selector("div.item ")

        browser.close()    
        return notebooks



ms = scrape_notebooks()
#for notebook in ms:
    #print(f"NOTEBOOK {notebook['N']}\n Nombre: {notebook['Nombre']}\n Precio: {notebook['Precio']}\n Cuotas: {notebook['Cuotas']}\n\n")
#import pandas as pd
df = pd.DataFrame(data)
#df.to_csv("datos.csv", index=False)
df.to_excel("datos.xlsx", index=False, engine='openpyxl')
#print(df)


from playwright.sync_api import sync_playwright
import pandas as pd

data = []
def scrape_notebooks():
    #START PLAYWRIGHT
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) #CHANGE TO TRUE IF WE DON'T WANT TO SEE THE BROWSER
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0")
        page = context.new_page()
        #OPEN PAGE WEB
        url = "https://www.venex.com.ar/pagina-inicial.htm"
        page.goto(url)

        page.wait_for_selector("h4.section-title.hidden-xs.mt1")
        #FIND THE BUTTON WITH THE NOTEBOOK LINKS AND CLICK IT
        page.locator("h4.section-title.hidden-xs.mt1").locator("a").click()
        page.wait_for_selector("div.product-box")

        items = page.locator("div.product-box")

        notebooks = []

        for i in range(items.count()):
            #DO CLICK IN THE FIRST PRODUCT
            items.nth(i).click()

            page.wait_for_selector("h1.tituloProducto.hidden-xs")
            #EXTRACT NAME, PRICE Y QUOTAS 
            nombre = page.locator("h1.tituloProducto.hidden-xs ").inner_text()
            precio = page.locator("div.textPrecio.text-green").inner_text()
            cuotas = page.locator("div.form-control.ui-autocomplete-input").inner_text()

            #I STORE THE DATA IN AN ARRAY   
            notebooks.append({"Nombre": nombre, "Precio": precio, "Cuotas": cuotas, "N": i+1})
            entry = {
                "Name": nombre,
                "Price": precio,
                "Quotas": cuotas
            }
            data.append(entry)
            #RETURN TO THE PREVIOUS PAGE
            page.go_back()

            #I WAIT FOR THE PRODUCTS TO BE LOADED AGAIN
            page.wait_for_selector("div.item ")

        browser.close()    
        return notebooks



df = pd.DataFrame(data)
df.to_csv("data.csv", index=False)
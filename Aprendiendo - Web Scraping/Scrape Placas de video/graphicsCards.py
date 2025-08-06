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

        page.wait_for_selector("span.li-title")
        #ENCUENTRA EL BOTON CON EL LINKS DE LAS NOTEBOOKS Y LO CLIQUEA
        page.query_selector_all("span.li-title")[2].click()
        page.wait_for_selector("div.col-container.col-xs-12.col-md-8.col-lg-8")
        items = page.locator("div.col-container.col-xs-12.col-md-8.col-lg-8")

        graphicsCards = []
        
        for i in range(items.count()):
            #HAGA CLICK EN EL PRIMER PRODUCTO
            items.nth(i).click()

            page.wait_for_selector("h1.tituloProducto.hidden-xs")
            #EXTRAER NOMBRE, PRECIO Y CUOTAS DE LA PAG
            nombre = page.locator("h1.tituloProducto.hidden-xs ").inner_text()
            precio = page.locator("div.textPrecio.text-green").inner_text()
            cuotas = page.locator("div.form-control.ui-autocomplete-input").inner_text()

            #ALMACENO LOS DATOS EN UN ARREGLO
            graphicsCards.append({"Nombre": nombre, "Precio": precio, "Cuotas": cuotas, "N": i+1})
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
        return graphicsCards


ms = scrape_notebooks()

df = pd.DataFrame(data)
output_file = "graphicsCards.xlsx"
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']

    # Ajustar el ancho de las columnas según el contenido
    for column_cells in worksheet.columns:
        max_length = 0
        column = column_cells[0].column_letter  # Obtener la letra de la columna
        for cell in column_cells:
            try:  # Asegurarse de manejar celdas vacías
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2  # Ajustar un poco más por estética
        worksheet.column_dimensions[column].width = adjusted_width
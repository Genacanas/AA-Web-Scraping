import requests
import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

# Función para obtener datos básicos de la API
def scrape_api_data():
    address = "1063 HIBISCUS ST"
    formatted_address = address.replace(" ", "%20").lower()
    url = f"https://www.bcpao.us/api/v1/search?address={formatted_address}&activeonly=true&sortcolumn=siteaddress&sortorder=asc&size=10&page=1"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://www.bcpao.us/',
        'Origin': 'https://www.bcpao.us'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()[0]
        result = {
            "Account": data.get("account"),
            "Owners": data.get("owners"),
            "Mail Address": data.get("mailAddress"),
            "Site Address": data.get("siteAddress"),
            "Parcel ID": data.get("parcelID"),
            "Property Use": data.get("landUseCode"),
            "Market Value": data.get("marketValue"),
            "Year Built": data.get("yearBuilt"),
            "Last Sale Date": data.get("saleDate"),
            "Last Sale Price": data.get("salePrice"),
        }
        print(json.dumps(result, indent=4))
        return data
    else:
        print("Error en la petición:", response.status_code)
        return None

# Función para obtener detalles adicionales con Playwright
def scrape_property_details(account):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        # Construcción de la URL para los detalles de la propiedad
        url_pw = f"https://www.bcpao.us/PropertySearch/#/account/{account}"
        page.goto(url_pw)

        # Esperar que cargue el contenido
        page.wait_for_selector("table#tSalesTransfers", timeout=10000)

        # Obtener el contenido HTML
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Obtener el código del sitio y la descripción del terreno
        site_code = soup.select("div.cssDetails_Top_Cell_Data")[8].text.strip()
        land_description = soup.select("div.cssDetails_Top_Cell_Data")[11].text.strip()

        # 🗃️ Obtener las ventas anteriores
        sales = []
        sales_table = soup.select_one("table#tSalesTransfers")

        if sales_table:
            rows = sales_table.select("tbody tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 4:
                    date = cells[0].text.strip()
                    price = cells[1].text.strip()
                    sales.append({"Date": date, "Price": price})

        browser.close()

        # Retornar datos obtenidos
        return {
            "Site Code": site_code,
            "Land Description": land_description,
            "Sales": sales
        }

# Ejecución del scraping
api_data = scrape_api_data()
if api_data:
    account = api_data.get("account")
    if account:
        details = scrape_property_details(account)
        print(json.dumps(details, indent=4))
